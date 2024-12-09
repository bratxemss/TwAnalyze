import customtkinter as ctk
import asyncio
import threading
from .extractor import XExtractor


class TwitterApp(ctk.CTk):
    def __init__(self):
        self.nickname = ""
        self.num_tweets = 0
        self.fetch_from_db = False
        self.extractor = None

        super().__init__()


        self.title("Twitter Data Fetcher")
        self.geometry("700x800")
        self.configure(padx=20, pady=20)

        self.title_label = ctk.CTkLabel(self, text="Twitter Data Fetcher", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=20)

        self.nickname_label = ctk.CTkLabel(self, text="Enter Nickname:", font=("Arial", 14))
        self.nickname_label.pack(anchor="w", pady=(10, 5))
        self.nickname_entry = ctk.CTkEntry(self, placeholder_text="Nickname", width=300)
        self.nickname_entry.pack(pady=5)

        self.db_fetch_var = ctk.BooleanVar(value=False)
        self.db_checkbox = ctk.CTkCheckBox(
            self, text="Fetch data from database", variable=self.db_fetch_var, font=("Arial", 12)
        )
        self.db_checkbox.pack(pady=10)

        self.tweets_label = ctk.CTkLabel(self, text="Number of Tweets:", font=("Arial", 14))
        self.tweets_label.pack(anchor="w", pady=(10, 5))
        self.tweets_entry = ctk.CTkEntry(self, placeholder_text="Number of Tweets", width=300)
        self.tweets_entry.pack(pady=5)

        self.text_output_label = ctk.CTkLabel(self, text="Generated Text:", font=("Arial", 14))
        self.text_output_label.pack(anchor="w", pady=(10, 5))
        self.text_output = ctk.CTkTextbox(self, height=250, width=500, corner_radius=10)
        self.text_output.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_button_clicked)
        self.submit_button.pack(pady=20)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

    async def fetch_data(self):
        self.nickname = self.nickname_entry.get()
        self.fetch_from_db = self.db_fetch_var.get()
        self.num_tweets = self.tweets_entry.get()


        if not self.nickname:
            return "Error: Nickname is required."

        try:
            self.num_tweets = int(self.num_tweets) if self.num_tweets else 30
        except ValueError:
            return "Error: Number of tweets must be a number."
        self.extractor = XExtractor(self.nickname, self.num_tweets, self.fetch_from_db)
        return await self.extractor.main()

    async def animate_progress_bar(self):
        while True:
            self.progress_bar.set((self.progress_bar.get() + 0.05) % 1)
            await asyncio.sleep(0.1)

    async def start_loading(self):
        self.submit_button.configure(state="disabled")
        self.progress_bar.set(0)
        animation_task = asyncio.create_task(self.animate_progress_bar())

        generated_text = await self.fetch_data()

        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass

        self.after(0, self.update_ui, generated_text)

    def update_ui(self, text):
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", text)
        self.progress_bar.set(1)
        self.submit_button.configure(state="normal")

    def run_async_task(self):
        def thread_target():
            asyncio.run(self.start_loading())
        threading.Thread(target=thread_target, daemon=True).start()

    def submit_button_clicked(self):
        self.run_async_task()
