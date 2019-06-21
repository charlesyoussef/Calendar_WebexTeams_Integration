//
// Command: help
//
module.exports = function (controller) {

    controller.hears(["help", "who"], 'direct_message,direct_mention', function (bot, message) {
        var text = "Here are the skills of Webex_Teams MEA_Calendar_Bot:";
        text += "\n- " + bot.enrichCommand(message, "about") + ": Shows metadata info about the bot.";
        text += "\n- " + bot.enrichCommand(message, "help") + ": Manual for the bot skills.";
        text += "\n- " + bot.enrichCommand(message, "event create") + ": Assists in submitting an event to MEA calendar.";
        text += "\n- " + bot.enrichCommand(message, "event list") + ": Lists the next 6 upcoming events in MEA calendar.";
        text += "\n- " + bot.enrichCommand(message, "event approve") + ": (Admin-only) Approves a submitted event in MEA calendar.";
        bot.reply(message, text);
    });
}
