parser grammar raw_keywords;

/* Raw keyword definitions, for references within other abilities. */

raw_keywords : raw_keyword
               ( ( COMMA! ( raw_keyword COMMA! )+ )? conj^ raw_keyword )? ;

// TODO: split these out so I can reference only the correct subsets
// for eg. equip costs?
raw_keyword : DEATHTOUCH
            | DEFENDER
              // Separate tokens for first and double strike.
            | DOUBLE STRIKE -> DOUBLE_STRIKE[]
            | FIRST STRIKE -> FIRST_STRIKE[]
            | ENCHANT
            | EQUIP
            | FLASH
            | FLYING
            | HASTE
            | HEXPROOF
            | INTIMIDATE
            | LIFELINK
            | PROTECTION
            | REACH
            | SHROUD
            | TRAMPLE
            | VIGILANCE
            | ABSORB
            | AFFINITY
            | AMPLIFY
            | ANNIHILATOR
              // Separate tokens for aura swap and bands with other.
            | AURA SWAP -> AURA_SWAP[]
            | BAND WITH OTHER -> BANDS_WITH_OTHER[]
            | BANDING
            | BATTLE_CRY
            | BLOODTHIRST
            | BUSHIDO
            | BUYBACK
            | CASCADE
            | CHAMPION
            | CHANGELING
            | CONSPIRE
            | CONVOKE
            | CUMULATIVE_UPKEEP
            | CYCLING
            | DEVOUR
            | DELVE
            | DREDGE
            | ECHO
            | ENTWINE
            | EPIC
            | EVOKE
            | EXALTED
            | FADING
            | FEAR
            | FLANKING
            | FLASHBACK
            | FORECAST
            | FORTIFY
            | FRENZY
            | GRAFT
            | GRAVESTORM
            | HAUNT
            | HIDEAWAY
            | HORSEMANSHIP
            | INFECT
            | KICKER
            | LANDWALK
              // Separate tokens for level up.
            | LEVEL UP -> LEVEL_UP[]
            | LIVING_WEAPON
            | MADNESS
            | MIRACLE
            | MODULAR
            | MORPH
            | MULTIKICKER
            | NINJUTSU
            | OFFERING
            | PERSIST
            | PHASING
            | POISONOUS
            | PROVOKE
            | PROWL
            | RAMPAGE
            | REBOUND
            | RECOVER
            | REINFORCE
            | REPLICATE
            | RETRACE
            | RIPPLE
            | SHADOW
            | SOULBOND
            | SOULSHIFT
            | SPLICE
            | SPLIT_SECOND
            | STORM
            | SUNBURST
            | SUSPEND
            | TOTEM_ARMOR
            | TRANSFIGURE
            | TRANSMUTE
            | UNDYING
            | UNEARTH
            | VANISHING
            | WITHER
            ;