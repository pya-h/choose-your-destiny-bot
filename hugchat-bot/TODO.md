# Write Readme.md
    Write a propper readme.md file

# Implement all Telegram api methods.
    * For now just some basic methods are implemented. need to implement others. Methods written up until now:
        1. sendMessage
        2. editMessageText
        3. answerCallbackQuery
        4. getUpdates (for longpolling bots)

    * Main methods that are required in any bot:
        1. sendPhoto
        2. sendDocument
        3. sendVideo
        4. sendAudio (or sendMusic?)
        5. sendVoice
        6. getChatMember
        7. sendChatAction [?]
        8. * Make Jobs async too.
        9. etc
        
# Chalenges
    * This bot works well on local devices, remote servers but not on a cpanel host.
    - The problem on cpanel, is in webhook mode, that its Job planner doesnt worn and it doesnt fire jobs at their due. [Think & R&D]

    * The passenger_wsgi application runs as expected but again, Planner doesnt work. I think it has something to do with being run as background process.
    
    * I want this to be more of a framework, or even a module. But for now its just a prepared python app that can be extended. [Needs R&D]