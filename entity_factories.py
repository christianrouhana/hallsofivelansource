from components.ai import HostileEnemy, RangedEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

"""player"""
player = Actor(
    char="@",
    color=(225,210,60),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)

"""enemies here"""
orc = Actor(
    char="o",
    color=(63,127,63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
#weak range type
goblin_archer = Actor(
    char="a",
    color=(63,127,63),
    name="Goblin Archer",
    ai_cls=RangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75)
)
troll = Actor(
    char="T",
    color=(63,127,63),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter = Fighter(hp=16, base_defense=1, base_power=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100)
)
jackal = Actor(
    char="j",
    color= (185, 155, 50),
    name="Jackal",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter = Fighter(hp=13, base_defense=0, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75)
)
goblin = Actor(
    char="g",
    color=(63,127,63),
    name="Goblin",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10,base_defense=1, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75)
)
#low level mid game, big threat early
drone = Actor(
    char="d",
    color=(255,153,153),
    name="Eldritch Steel Drone",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=18,base_defense=2, base_power=6),
    inventory=Inventory(capacity=0),
    level=Level(xp_given = 125)
)
# mid level mid game
guardian = Actor(
    char="G",
    color=(110,190,200),
    name="Eldritch Guardian",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=2, base_power=9),
    inventory=Inventory(capacity=0),
    level=Level(xp_given = 195)
)
#hope you dont run into this early on
warden = Actor(
    char="W",
    color=(255,255,135),
    name="Possessed Warden",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=25, base_defense=5, base_power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=210)
)

#strong range type
beam_soldier = Actor(
    char="b",
    color=(255,255,255),
    name="Eldritch Beam Warrior",
    ai_cls=RangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=2, base_power=9),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=210)
)

corrupted_wizard = Actor(
    char="w",
    color=(255,0,230),
    name="Wizard, follower of Ivelan",
    ai_cls=RangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=35, base_defense=5, base_power=11),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=270)
)
#evil tank
enchanted_statue = Actor(
    char="s",
    color=(255,255,255),
    name="Enchanted Statue",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=40, base_defense=8, base_power=17),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=330),
)
agent_of_ivelan = Actor(
    char="A",
    color=(255,255,255),
    name="Demonic Agent of Ivelan",
    ai_cls=RangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=45, base_defense=7, base_power=16),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=500),
)
monolith = Actor(
    char="M",
    color=(255,255,255),
    name="Monolith, Incomprehensible Evil",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=70, base_defense=12, base_power=25),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=1000),
)
"""consumables"""
health_potion = Item(
    char="!",
    color=(0,160,255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
trick_health_potion = Item(
    char="!",
    color=(0,160,255),
    name="Bubbling Health Potion",
    consumable=consumable.TrickHealing(amount=-3),
)
super_health_potion = Item(
    char="+",
    color=(0,160,255),
    name="Super Potion",
    consumable=consumable.HealingConsumable(amount=10),
)
ultra_health_potion = Item(
    char="%",
    color=(0,160,255),
    name="Ultra Potion",
    consumable=consumable.HealingConsumable(amount=18),
)
fireball_scroll=Item(
    char="~",
    color=(255,55,0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage = 12, radius = 3),
)
lightning_scroll = Item(
    char="~",
    color=(225,200,0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, max_range=5),
)
confusion_scroll = Item(
    char="~",
    color=(190, 150, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
defense_potion = Item(
    char="!",
    color=(0,150,15),
    name="Defense Potion",
    consumable=consumable.DefenseConsumable(amount=3, number_of_turns=10)
)
trick_defense_potion = Item(
    char = "!",
    color= (0,150,15),
    name = "Murky Defense Potion",
    consumable=consumable.DefenseConsumable(amount=-2, number_of_turns=10)
)
power_potion = Item(
    char="!",
    color=(210,80,200),
    name="Power Potion",
    consumable=consumable.PowerConsumable(amount=3, number_of_turns=10)
)
trick_power_potion = Item(
    char="!",
    color=(210,80,200),
    name="Old Power Potion",
    consumable=consumable.PowerConsumable(amount=-3, number_of_turns=10)
)
beam_rune = Item(
    char="`",
    color = (140,140,140),
    name="Beam Rune",
    consumable=consumable.BeamConsumable(damage=25)
)
old_bow = Item(
    char="/",
    color = (100, 60, 53),
    name="Old Bow and One(??) Arrow",
    consumable=consumable.BowConsumable(damage=10)
)
time_stop_scroll = Item(
    char="~",
    color=(170,0,200),
    name="Time Scroll",
    consumable=consumable.TimeStopConsumable(number_of_turns=10, radius=3),
)
#staffs do not break on consumption, good item
lesser_staff = Item(
    char="/",
    color=(140,120,60),
    name="Lesser Staff",
    consumable=consumable.Staff(damage=12),
)
explosive_staff = Item(
    char="/",
    color=(160,140,80),
    name="Explosive Staff",
    consumable=consumable.ExplosiveStaff(damage=15,radius=3),
)
#end game staff
end_staff = Item(
    char="/",
    color=(180,160,100),
    name="Ivelan's Staff of Corruption",
    consumable=consumable.EndStaff(damage=25,radius=3),
)

dagger = Item(
    char="/",
    color=(79, 79, 79),
    name="Dagger",
    equippable=equippable.Dagger()
)

sword = Item(
    char="/",
    color=(79, 79, 79),
    name="Iron Sword",
    equippable=equippable.Sword()
)
diamond_sword=Item(
    char="/",
    color=(0, 200, 180),
    name="Diamond Sword",
    equippable=equippable.DiamondSword()
)
adamantine_sword=Item(
    char="/",
    color=(0, 80, 80),
    name="Adamantine Sword",
    equippable=equippable.AdamantineSword()
)
beam_sword = Item(
    char="/",
    color=(150, 100, 0),
    name="Beam Sword",
    equippable=equippable.BeamSword()
)

leather_armor = Item(
   char="[",
   color=(150, 90, 0),
   name="Leather Armor",
   equippable=equippable.LeatherArmor(),
)
chain_mail = Item(
    char="[",
    color=(175, 175, 175),
    name="Chain Mail",
    equippable=equippable.ChainMail()
)
knight_armor = Item(
    char="[",
    color=(200, 200, 200),
    name="Knight Armor",
    equippable=equippable.KnightArmor()
)
adamantine_armor = Item(
    char="[",
    color=(150, 100, 0),
    name="Adamantine Armor",
    equippable=equippable.AdamantineArmor()
)
runic_armor = Item(
    char="[",
    color=(255, 170, 0),
    name="Runic Armor",
    equippable=equippable.RunicArmor()
)
