import os
import telebot
import speech_recognition
from pydub import AudioSegment


# Токен, который дал BotFather при регистрации
token = ...

bot = telebot.TeleBot(token)


def oga2wav(filename):
    # Конвертация формата файлов
    new_filename = filename.replace('.oga', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format='wav')
    return new_filename


def recognize_speech(oga_filename):
    # Перевод голоса в текст + удаление использованных файлов
    wav_filename = oga2wav(oga_filename)
    recognizer = speech_recognition.Recognizer()

    with speech_recognition.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    text = recognizer.recognize_google(wav_audio, language='ru')

    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text


def download_file(bot, file_id):
    # Скачивание файла, который прислал пользователь
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


# Все функции общения приложения с ТГ спрятаны в функции под @
@bot.message_handler(commands=['start'])
def say_hi(message):
    bot.send_message(message.chat.id,
     ('Привет, ' +
      str(message.chat.first_name) +
      '! Это бот для распознавания речи.' +
      '\nОтправь свое голосовое сообщение и бот распознает его.'))

# Отправляем стикер
@bot.message_handler(commands=['send_sticker'])
def send_python_sticker(message):
    filename = open('/content/python_sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, filename)


@bot.message_handler(content_types=['voice'])
def transcript(message):
    # Функция, отправляющая текст в ответ на голосовое
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)


# Запускаем бота
bot.polling()
