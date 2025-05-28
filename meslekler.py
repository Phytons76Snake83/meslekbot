

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
    job = None   #  sistemi başlangıcı

    await ctx.send("İlk başta en klasik sorulardan biri... Sözel hafızan daha iyi ise 1'i, sayısal hafızan daha iyi ise 2'yi tuşlayın. (20 saniyen var!)")

    def kontrol(mesaj):
        return mesaj.author == ctx.author and mesaj.channel == ctx.channel

    try:
        cevap = await bot.wait_for("message", check=kontrol, timeout=20.0)
        user_point = int(cevap.content)

        if user_point not in [1, 2]:
            await ctx.send("Keşke soruya uygun bir cevap verseydin. Şu andan itibaren tekrar başlamak zorundasın.")
            return

        if user_point == 1:
            point += 1
        elif user_point == 2:
            point += 100

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

        if user_point == 1:
            point += 55
        elif user_point == 2:
            point += 25

    except asyncio.TimeoutError:
        await ctx.send("Yanıt vermekte geç kaldın.")
        return
    

    await ctx.send("Son soru. Şimdi sana söyleyeceklerimden hangisini tercih edersin? İnsanlara yardım etmek, boş vaktinde arkadaşlarınla sohpet etmek, empati kurallarına uymak veya etik davranmayı tercih edersen 1'i; Hafızanı kullanarak gördüğün şeyleri hatırlamak, dürüst olmak, akıllı olmak veya kararlı olmak için 2'yi tuşlayın.")

    try:
        cevap = await bot.wait_for("message", check=kontrol, timeout=20.0)
        user_point = int(cevap.content)

        if user_point not in [1, 2]:
            await ctx.send("Keşke soruya uygun bir cevap verseydin. Şu andan itibaren tekrar başlamak zorundasın.")
            return

        if user_point == 1:
            point += 71
        elif user_point == 2:
            point += 65

    except asyncio.TimeoutError:
        await ctx.send("Yanıt vermekte geç kaldın.")
        return
    
    if point == 127 :
        job = "Yazar"
    if point == 121 :
        job = "Psikolog"
    if point == 226:
        job = "Doktor"
    if point == 220:
        job = "Mühendis"
    if point == 97:
        job = "Öğretmen"
    if point == 190:
        job = "Vali"
    if point == 91:
        job = "Şef"
    if point == 191:
        job = "Pilot"

    await ctx.send("Test başarıyla sonuşlandı! Sırf insanları heyecanlandırmak için alttaki butona tıklayarak öğrenebilirsiniz:)")

    button = Button(label="HEYYYY! Buradayımmm.", style=discord.ButtonStyle.primary)

    async def callback(interaction):
        await interaction.response.send_message(
            f"Tabii ki senin mesleğinnnnn... {job}. Eğer istersen !foto komutu ile de yüzüne uygulayabilirsin maskeni.",
            ephemeral=True
    )

    button.callback = callback

    view = View()
    view.add_item(button)

    await ctx.send("Butona basmak ister misin?", view=view)


    
    
   

bot.run(token)