import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

API_TOKEN = "7502578588:AAEucIcb_FUQOowBrnMyknsy5Mqc_KBZufY"
ADMIN_IDS = [6677489688, 6433016654, 7043011107]  # ✅ All admins listed here
DATA_FILE = "channels.json"

# ✅ Load channel data
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"source": None, "targets": []}

# ✅ Save channel data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ✅ Admin check function
def is_admin(user_id):
    return int(user_id) in ADMIN_IDS

# 📦 Add source channel
async def add_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    try:
        source_id = int(context.args[0])
        data = load_data()
        data["source"] = source_id
        save_data(data)
        await update.message.reply_text(f"✅ Source channel set to {source_id}")
    except:
        await update.message.reply_text("⚠️ Usage: /addsource <chat_id>")

# 🎯 Add target channel
async def add_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    try:
        target_id = int(context.args[0])
        data = load_data()
        if target_id not in data["targets"]:
            data["targets"].append(target_id)
            save_data(data)
        await update.message.reply_text(f"✅ Target channel added: {target_id}")
    except:
        await update.message.reply_text("⚠️ Usage: /addtarget <chat_id>")

# ❌ Remove target
async def remove_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    try:
        target_id = int(context.args[0])
        data = load_data()
        if target_id in data["targets"]:
            data["targets"].remove(target_id)
            save_data(data)
            await update.message.reply_text(f"❌ Target channel removed: {target_id}")
        else:
            await update.message.reply_text("⚠️ Channel not found in targets.")
    except:
        await update.message.reply_text("⚠️ Usage: /removetarget <chat_id>")

# 📋 Show list
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    data = load_data()
    await update.message.reply_text(f"📡 Source: {data['source']}\n🎯 Targets: {data['targets']}")

# 🔁 Forwarder
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    source_id = data["source"]
    targets = data["targets"]

    if update.effective_chat.id != source_id:
        return

    msg = update.effective_message

    for tgt in targets:
        try:
            if msg.text:
                await context.bot.send_message(tgt, msg.text)
            elif msg.photo:
                await context.bot.send_photo(tgt, msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await context.bot.send_video(tgt, msg.video.file_id, caption=msg.caption or "")
            elif msg.document:
                await context.bot.send_document(tgt, msg.document.file_id, caption=msg.caption or "")
            elif msg.sticker:
                await context.bot.send_sticker(tgt, msg.sticker.file_id)
        except Exception as e:
            print(f"❌ Error forwarding to {tgt}: {e}")

# 🔁 Main
def main():
    app = ApplicationBuilder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("addsource", add_source))
    app.add_handler(CommandHandler("addtarget", add_target))
    app.add_handler(CommandHandler("removetarget", remove_target))
    app.add_handler(CommandHandler("showlist", show_list))

    app.add_handler(MessageHandler(filters.ALL, forward_message))

    print("📡 Dynamic Forward Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
