import asyncio
import random  
from twitchio.ext import commands
import tkinter as tk

BOT_NICK = 'bernardhito'
TOKEN = 'p31xth14louih3kdd3ksi0nmrwrmbp'
DEFAULT_CHANNEL = 'BiigRushh'
DEFAULT_START_NUMBER = 11019


class Bot(commands.Bot):

    def __init__(self, channel=DEFAULT_CHANNEL, start_number=DEFAULT_START_NUMBER):
        super().__init__(token=TOKEN, prefix='!', initial_channels=[channel])
        self.running = False
        self.count_task = None
        self.channel = channel
        self.current_number = start_number
        self.update_callback = None

    async def event_ready(self):
        print(f'Bot {self.nick} está pronto e conectado a {self.channel}!')
        if self.running:
            if self.count_task is None:
                self.count_task = asyncio.create_task(self.count_and_send_numbers())

    async def count_and_send_numbers(self):
        for number in range(self.current_number, 1000001):
            if not self.running:
                self.current_number = number
                break
            print(f'Enviando número: {number}')
            try:
                await self.send_number(number)
                
                if self.update_callback:
                    self.update_callback(number)
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                break
            
            
            random_delay = random.randint(2, 5)
            await asyncio.sleep(random_delay)
        
        self.current_number = 11019  

    async def send_number(self, number):
        channel = self.get_channel(self.channel)
        if channel:
            try:
                await channel.send(str(number))
                print(f'Mensagem enviada: {number}')
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                raise
        else:
            print(f"Canal {self.channel} não encontrado.")

    async def start_bot(self):
        if not self.running:
            self.running = True
            try:
                await self.start()
            except Exception as e:
                print(f"Erro ao iniciar o bot: {e}")
                await self.stop_bot()

    async def stop_bot(self):
        if self.running:
            self.running = False
            if self.count_task:
                self.count_task.cancel()
                self.count_task = None
            try:
                if self._connection and not self._connection._closed:
                    await self._connection._close()
                await self.close()
            except Exception as e:
                print(f"Erro ao parar o bot: {e}")

    def update_channel(self, new_channel):
        self.channel = new_channel
        
        if self.running:
            if self.count_task:
                self.count_task.cancel()
            self.count_task = asyncio.create_task(self.count_and_send_numbers())

    def set_update_callback(self, callback):
        self.update_callback = callback


class BotApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.bot = None
        self.loop = asyncio.get_event_loop()
        self.title("Controle do Bot da Twitch")
        self.geometry("400x300")

        self.channel_entry = tk.Entry(self)
        self.channel_entry.insert(0, DEFAULT_CHANNEL)
        self.channel_entry.pack(pady=10)

        self.start_number_entry = tk.Entry(self)
        self.start_number_entry.insert(0, str(DEFAULT_START_NUMBER))
        self.start_number_entry.pack(pady=10)

        self.update_channel_button = tk.Button(self, text="Atualizar Canal", command=self.update_channel)
        self.update_channel_button.pack(pady=10)

        self.start_button = tk.Button(self, text="Ligar Bot", command=self.start_bot)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Desligar Bot", command=self.stop_bot)
        self.stop_button.pack(pady=10)

        self.status_label = tk.Label(self, text="Bot Desligado", fg="red")
        self.status_label.pack(pady=10)

        self.history_label = tk.Label(self, text="Número atual: 11019")
        self.history_label.pack(pady=10)

    def start_bot(self):
        if not self.bot or not self.bot.running:
            if self.bot and self.bot.running:
                self.loop.create_task(self.bot.stop_bot())
                self.bot = None
            start_number = int(self.start_number_entry.get())
            self.status_label.config(text="Bot Ligado", fg="green")
            self.bot = Bot(self.channel_entry.get(), start_number)
            self.bot.set_update_callback(self.update_history_label)  
            self.loop.create_task(self.bot.start_bot())

    def stop_bot(self):
        if self.bot and self.bot.running:
            self.status_label.config(text="Bot Desligado", fg="red")
            self.loop.create_task(self.bot.stop_bot())

    def update_channel(self):
        if self.bot:
            new_channel = self.channel_entry.get()
            try:
                self.bot.update_channel(new_channel)
                self.status_label.config(text="Canal atualizado com sucesso!", fg="green")
            except Exception as e:
                self.status_label.config(text=f"Erro: {e}", fg="red")
        else:
            self.status_label.config(text="Bot não está rodando.", fg="red")

    def update_history_label(self, number):
        self.history_label.config(text=f"Número atual: {number}")


async def main():
    app = BotApp()

    while True:
        app.update()
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
