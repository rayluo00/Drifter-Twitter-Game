    DRIFTER TWITTER GAME
    Western Washington University
    CSCI 497H/597H - Human-Centered System Design

    Authors : Raymond Weiming Luo
              Zachary McGrew
              HildigerR Vergaray
              Sereyvathanak Khorn

    ==================================================================================
                                        DESCRIPTION
    ==================================================================================
    
        Drifter is a M.U.D style game that uses the Twitter API to collect tweets from
    users as in-game commands. A Twitter bot is hosted and will post a photo of the
    game's status along with a description of what has happened in-game. The game
    utilizes a mechanic considered as a "demoncracy system" similar to the concept
    for Twitch Plays Pokemon. The most popular tweet from unique users of which command
    to perform will be used. A regex is implemented to allow variations of tweets that
    would correlate to the same command (i.e. 'harvest', 'HARVEST', 'haRvEst',
    'harVEST').

    ==================================================================================
                                     LIST OF COMMANDS
    ==================================================================================
    * oribt [Planet #]                  = Orbits the specified planet.
    * depart                            = Leave the current planet.
    * drift                             = Drift to a random location in space.
    * home                              = Use all fuel resources to travel home.
    * harvest                           = Chance to harvest resources on planet.
    * jettison [Item count] [Item name] = Destorys the amount of items provided.
    * buy [Item count] [Item name]      = Buy items from civilization.
    * sell [Item count] [Item name]     = Sell items in inventory.
    * attack                            = Attack the civilization.
    * refine [Item count] [Item name]   = Refine item if requirements are met.
    * gamble [Amount to bet]            = Chance to gamble in a civilization.
    * repair                            = Repair the ship if requirements are met.
    * craft [Item count] [Item name]    = Craft the item if requirements are met.
    