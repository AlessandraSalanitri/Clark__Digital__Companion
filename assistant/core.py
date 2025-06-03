import base64
from assistant.intent_router import detect_intent
from assistant.modules import ocr, time_module, weather, web, calendar_module, trainline
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from assistant.modules import crossing
from camera import webcam


class Assistant:
    def __init__(self, model):
        self.chat_history = ChatMessageHistory() #shared memory
        self.chat_chain = self._create_chat_chain(model)
        self.vision_chain = self._create_vision_chain(model)
        
        self.last_intent = None
        self.last_user_prompt = ""


    def _create_chat_chain(self, model):
        SYSTEM_PROMPT = """
        You are a witty and friendly assistant named Clark. 
        You are built to help and emotionally support visually impaired users. 
        Your primary goals:
        - Answer questions as clearly and concisely as possible
        - If the user expresses negative emotions like "I'm sad", "I feel lonely", "I'm anxious", your job is to be emotionally supportive, reassuring, and helpful.
        - Acknowledge their feeling first. Then uplift them or offer help.
        - Always sound compassionate, thoughtful, and warm.

        Avoid giving long therapy sessions, be brief but sincere.
        """

        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{prompt}"),
        ])

        chain = prompt_template | model | StrOutputParser()

        return RunnableWithMessageHistory(
            chain,
            lambda _: self.chat_history, # shared
            input_messages_key="prompt",
            history_messages_key="chat_history"
        )

    def _create_vision_chain(self, model):
        SYSTEM_PROMPT = """You are Clark, a visual assistant. Describe or answer based on user prompt and image."""

        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                [
                    {"type": "text", "text": "{prompt}"},
                    {"type": "image_url", "image_url": "data:image/jpeg;base64,{image_base64}"},
                ],
            ),
        ])

        chain = prompt_template | model | StrOutputParser()

        return RunnableWithMessageHistory(
            chain,
            lambda _: self.chat_history, #shared
            input_messages_key="prompt",
            history_messages_key="chat_history"
        )


    def handle(self, prompt, image_b64):
        try:
            
            if self.last_intent == "awaiting_trip_type":
                updated_prompt = self.last_user_prompt + " " + prompt
                response_text = trainline.book_train_ticket(updated_prompt)
                self.last_intent = None  # clear state
                return {"text": response_text}

            intent = detect_intent(prompt)

            # OCR / Vision requests must have camera input
            if intent in ["vision", "ocr"] and not image_b64:
                return {"text": "Sorry, I need the camera input to answer that."}

            # VISION
            if intent == "vision":
                response = self._chat(prompt, image_b64, intent="vision")
                return {"text": response}

            # OCR
            elif intent == "ocr":
                response = ocr.read_text_from_image(image_b64)
                return {"text": response}

            # CROSSING DETECTION
            elif intent == "crossing":
                response = crossing.analyze_crossing(image_b64)
                return {"text": response}

            # TIME
            elif intent == "time":
                return {"text": time_module.get_time()}

            # WEATHER
            elif intent == "weather":
                return {"text": weather.get_weather(prompt)}

            # WEB ACTIONS
            elif intent == "web":
                result = web.perform_web_action(prompt)
                if isinstance(result, dict):
                    if "amazon_results" in result:
                        self.last_results = result["amazon_results"]
                        return {
                            "text": "Clark found some items. Would you like the top five or the cheapest?",
                            "amazon_results": self.last_results
                        }
                    elif "google_summary" in result:
                        self.last_summary = result["google_summary"]
                        return {"text": "I've found a summary. Want me to read it?"}
                return {"text": str(result)}

            # CALENDAR
            elif intent == "calendar":
                from controllers.calendar_controller import clark_handle_calendar
                return clark_handle_calendar(prompt)


            # TRAIN
            elif intent == "train":
                self.last_user_prompt = prompt
                response_text = trainline.book_train_ticket(prompt)

                if response_text == "awaiting_trip_type":
                    self.last_intent = "awaiting_trip_type"
                    return {"text": "Would you like a one-way ticket, a return, or an open return?"}

                return {"text": response_text}


            elif intent == "train-confirm":
                return {"text": trainline.confirm_train_booking()}

            # AMAZON FOLLOW-UPS (Web context)
            elif hasattr(self, "last_results") and self.last_results:
                lowered = prompt.lower()
                import re

                # 1. List the cheapest
                if "cheapest" in lowered:
                    try:
                        cheapest = min(
                            self.last_results,
                            key=lambda x: float(x["price"].replace("$", "").replace(",", ""))
                            if x["price"] != "Unknown" else float('inf')
                        )
                        self.selected_amazon_item = cheapest  # store for later
                        
                        return {
                            "text": f"The cheapest is: {cheapest['title']} for {cheapest['price']} with rating {cheapest['rating']}"
                        }
                    except Exception as e:
                        print("[Follow-up error - cheapest]", e)
                        return {"text": "Sorry, I couldn’t determine the cheapest option."}

                # 2. List the top 5
                elif "top 5" in lowered or "best" in lowered:
                    top_items = self.last_results[:5]
                    lines = [
                        f"Number {i+1}: {item['title']} - {item['price']} - {item['rating']} stars"
                        for i, item in enumerate(top_items)
                    ]
                    return {"text": "Here are the top 5:\n" + "\n".join(lines)}

                # 3. Specific item by number
                elif re.search(r"\bnumber\s*(\d+)\b", lowered):
                    index = int(re.search(r"\bnumber\s*(\d+)\b", lowered).group(1)) - 1
                    if 0 <= index < len(self.last_results):
                        selected = self.last_results[index]
                        self.selected_amazon_item = selected  # store selection
                        web.confirm_amazon_checkout()  # simulate confirmation
                        return {
                            "text": f"You selected item number {index+1}: {selected['title']} for {selected['price']}. It's added to cart!"
                        }
                    else:
                        return {"text": "I couldn’t find that item number."}

                # 4. Add to cart / basket follow-up
                elif intent == "amazon-add":
                    if hasattr(self, "selected_amazon_item") and self.selected_amazon_item:
                        try:
                            item = self.selected_amazon_item
                            web.confirm_amazon_checkout()  # simulate
                            return {
                                "text": f"Added {item['title']} to your Amazon cart. (Simulated)"
                            }
                        except Exception as e:
                            print("[Cart Add Error]", e)
                            return {"text": "I couldn’t add that to the cart, something went wrong."}
                    else:
                        return {"text": "I’m not sure which item you meant. Please say 'cheapest' or 'number 1' again."}


            # Google summary follow-up
            if hasattr(self, "last_summary") and ("yes" in prompt or "summarize" in prompt):
                return {"text": self.last_summary[0]}

            # DEFAULT CHAT
            return {"text": self._chat(prompt, image_b64, intent="chat")}

        except Exception as e:
            print("Clark error:", e)
            return {"text": "Sorry, I can't do this at the moment."}



    def _chat(self, prompt, image_b64="", intent="chat"):
        try:
            if intent in ["vision"]:  # Use vision chain
                image_data = image_b64 if image_b64 else ""
                response = self.vision_chain.invoke({
                    "prompt": prompt,
                    "image_base64": image_data
                }, config={"configurable": {"session_id": "user"}})
                return response.strip()

            # Fallback to text-only chat
            response = self.chat_chain.invoke({
                "prompt": prompt
            }, config={"configurable": {"session_id": "user"}})
            return response.strip()

        except Exception as e:
            print("Clark Chat failed:", e)
            if intent in ["vision", "ocr"]:
                return "Sorry, I couldn't analyze the camera input."
            return "Sorry, I didn't quite get that. Could you repeat?"
