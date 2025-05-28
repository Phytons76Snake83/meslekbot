import discord
from discord.ext import commands
import os
import cv2
import numpy as np
from PIL import Image
import sqlite3
import asyncio
from discord.ui import Button, View
from config import token, job

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Klasör ayarları
SAVE_FOLDER = "saved_images"
MASK_PATH = os.path.join(SAVE_FOLDER, "mask.png")
PHOTO_INPUT_PATH = os.path.join(SAVE_FOLDER, "photo_input.jpg")
PHOTO_OUTPUT_PATH = os.path.join(SAVE_FOLDER, "filtered_face.png")
os.makedirs(SAVE_FOLDER, exist_ok=True)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def oluştur(ctx):
    point = 0

    await ctx.send(
        "İlk başta en klasik sorulardan biri... Sözel hafızan daha iyi ise 1'i, "
        "sayısal hafızan daha iyi ise 2'yi tuşlayın. (20 saniyen var!)"
    )

    def kontrol(mesaj):
        return mesaj.author == ctx.author and mesaj.channel == ctx.channel

    try:
        cevap = await bot.wait_for("message", check=kontrol, timeout=20.0)
        user_point = int(cevap.content)

        if user_point not in [1, 2]:
            await ctx.send("Keşke soruya uygun bir cevap verseydin. Şu andan itibaren tekrar başlamak zorundasın.")
            return

        point += 1 if user_point == 1 else 100

    except asyncio.TimeoutError:
        await ctx.send("Yanıt vermekte geç kaldın.")
        return

    await ctx.send("Sonraki soru. Kitap okumayı seviyor musun? Seviyorsan 1'i, sevmiyorsan 2'yi tuşla.")

    try:
        cevap = await bot.wait_for("message", check=kontrol, timeout=20.0)
        user_point = int(cevap.content)

        if user_point not in [1, 2]:
            await ctx.send("Keşke soruya uygun bir cevap verseydin. Şu andan itibaren tekrar başlamak zorundasın.")
            return

        point += 55 if user_point == 1 else 25

    except asyncio.TimeoutError:
        await ctx.send("Yanıt vermekte geç kaldın.")
        return

    await ctx.send(
        "Son soru. Söylediklerimden hangisini tercih edersin?\n"
        "İnsanlara yardım etmek, arkadaşlarınla sohbet etmek, empati kurmak veya etik davranmak için 1'i;\n"
        "hafızanı kullanmak, dürüst olmak, akıllı olmak veya kararlı olmak için 2'yi tuşla."
    )

    try:
        cevap = await bot.wait_for("message", check=kontrol, timeout=20.0)
        user_point = int(cevap.content)

        if user_point not in [1, 2]:
            await ctx.send("Keşke soruya uygun bir cevap verseydin. Şu andan itibaren tekrar başlamak zorundasın.")
            return

        point += 71 if user_point == 1 else 65

    except asyncio.TimeoutError:
        await ctx.send("Yanıt vermekte geç kaldın.")
        return

    global job
    job = None
    if point == 127:
        job = "Yazar"
    elif point == 121:
        job = "Hakim"
    elif point == 226:
        job = "Doktor"
    elif point == 220:
        job = "Mühendis"
    elif point == 97:
        job = "Öğretmen"
    elif point == 190:
        job = "Vali"
    elif point == 91:
        job = "Şef"
    elif point == 191:
        job = "Pilot"

    await ctx.send(
        "Test başarıyla sonuçlandı! Sırf insanları heyecanlandırmak için alttaki butona tıklayarak öğrenebilirsiniz."
    )

    button = Button(label="HEYYY! İnsanları heyecanda bırakmak isteyen buton benim.", style=discord.ButtonStyle.primary)

    async def callback(interaction):
        await interaction.response.send_message(
            f"Tabii ki senin mesleğinnnnn... {job}. Eğer istersen !foto komutu ile de yüzüne uygulayabilirim maskeni.",
            ephemeral=True
        )

    button.callback = callback

    view = View()
    view.add_item(button)

    await ctx.send("Bakalım gerçeklerle yüzleşebilecek kadar cesur musun?", view=view)

@bot.command()
async def foto(ctx):
    if not ctx.message.attachments:
        await ctx.send("Lütfen filtrelenecek bir fotoğraf ekleyin.")
        return

    await ctx.message.attachments[0].save(PHOTO_INPUT_PATH)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    mask_path = f"saved_images/{job}.png"
    mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)

    img = cv2.imread(PHOTO_INPUT_PATH)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
    # Maske biraz daha büyük olsun:
        # Genel vücut genişliği ve yüksekliği
        body_width = img.shape[1]
        body_height = img.shape[0]

        # Maske genişliğini ve yüksekliğini vücuda göre ayarla
        mask_width = int(body_width * 0.6)  # omuz genişliğine göre ayarlıyoruz
        mask_height = int(body_height * 0.6)  # gövde yüksekliğine göre ayarlıyoruz

        # Maske yeri: yüzün altından başlasın
        y_offset = y + h  # yüzün altı
        x_offset = int((body_width - mask_width) / 2)  # ortaya hizala

        # Maske boyutlandır
        resized_mask = cv2.resize(mask, (mask_width, mask_height))

        # Maske yerleştirme
        for i in range(mask_height):
            for j in range(mask_width):
                y_pos = y_offset + i
                x_pos = x_offset + j

                if y_pos >= img.shape[0] or x_pos >= img.shape[1]:
                    continue

                if resized_mask[i, j, 3] > 0:  # alpha kanalı > 0 ise
                    img[y_pos, x_pos] = resized_mask[i, j][:3]

    cv2.imwrite(PHOTO_OUTPUT_PATH, img)
    await ctx.send(file=discord.File(PHOTO_OUTPUT_PATH))

@bot.command()
async def info(ctx):
    await ctx.send(
        "**Ben Meslek Bot!**\n\n"
        "Sana karakter özelliklerine göre en uygun mesleği bulmaya yardımcı olurum. "
        "Seçtiğin mesleğe uygun üniforma veya maskeyi fotoğrafına ekleyerek seni heyecanlandırırım! "
        "Ayrıca, Discord’da bana kolayca öneri ya da şikayetlerini yazabilirsin. "
        "Bu sayede eksiklerimi tamamlayıp yeni özellikler eklemeyi çok seviyorum.\n\n"
        "**Komutlarım:**\n"
        "• `!oluştur` → Karakter testini başlatır ve senin mesleğini bulurum.\n"
        "• `!foto` → Bulduğum mesleğe uygun maskeyi veya kıyafeti fotoğrafına eklerim.\n"
        "• `!önveşik [mesaj]` → Bana öneri ya da şikayetlerini iletebilirsin.\n"
        "• `!info` → Bu bilgileri sana tekrar hatırlatırım.\n\n"
        "Hep seninle olmaktan mutluyum! Geri bildirimlerinle beni daha da iyi hale getirebilirsin."
    )

@bot.command()
async def önveşik(ctx, *, mesaj=None):
    kullanici = str(ctx.author)

    if not mesaj:
        await ctx.send("Lütfen koddan sonraki alana öneri ve şikayetlerinizi yazın.")
        return

    conn = sqlite3.connect('oneri_ve_sikayetler.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO oneriler (kullanici, mesaj) VALUES (?, ?)", (kullanici, mesaj))
    conn.commit()
    conn.close()

    await ctx.send("Geri bildiriminiz kaydedildi. Teşekkürler!")

bot.run(token)
