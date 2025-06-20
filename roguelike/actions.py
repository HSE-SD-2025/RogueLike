def handle_base_actions(game):
    print(f"Quest: {game.quest.description} (Status: {game.quest.status})")
    if game.quest.status == 'artifact_found':
        print("You return to base with an artifact! Quest complete. Reward: Medkit.")
        game.player.add_item("Medkit")
        game.quest.reset()
    print("Actions: 1) Rest 2) Return to Zone 3) Equip Item 4) Unequip 5) Save Game 6) Quit")
    action = input("Choose action: ")
    if action == '1':
        game.player.hp = game.player.max_hp
        game.player.radiation = 0
        print("You rest at the base. HP and radiation fully restored.")
    elif action == '2':
        game.current_sector = game.world.generate_sector()
    elif action == '3':
        item = input("Enter item name to equip: ")
        if game.player.equip_item(item):
            print(f"Equipped {item}.")
        else:
            print("Item not found or not equippable.")
    elif action == '4':
        slot = input("Unequip 'weapon' or 'armor'?: ")
        if game.player.unequip_item(slot):
            print(f"Unequipped {slot}.")
        else:
            print("Nothing to unequip in that slot.")
    elif action == '5':
        from roguelike.persistence import save_game
        save_game(game.to_dict(), game.SAVE_FILE)
        print("Game saved!")
    elif action == '6':
        print("You leave the Zone...")
        return False
    else:
        print("Invalid action.")
    return True

def handle_item_pickup(game):
    if game.current_sector.get('item'):
        print(f"You see an item: {game.current_sector['item']}")
        pick = input(f"Pick up {game.current_sector['item']}? (y/n): ")
        if pick.lower() == 'y':
            game.player.add_item(game.current_sector['item'])
            print(f"You picked up {game.current_sector['item']}.")
            game.current_sector['item'] = None

def handle_artifact_pickup(game):
    if game.current_sector.get('artifact'):
        print(f"You see a rare artifact: {game.current_sector['artifact']}")
        pick = input(f"Pick up {game.current_sector['artifact']}? (y/n): ")
        if pick.lower() == 'y':
            game.player.add_artifact(game.current_sector['artifact'])
            print(f"You picked up {game.current_sector['artifact']}.")
            game.current_sector['artifact'] = None
            game.quest.mark_found()

def handle_anomaly_encounter(game):
    if game.current_sector['anomaly']:
        anomaly_type = game.current_sector.get('anomaly_type')
        from roguelike.world import ANOMALY_TYPES
        import random
        anomaly_info = next((a for a in ANOMALY_TYPES if a[0] == anomaly_type), None)
        print(f"There is an anomaly here: {anomaly_type}!")
        if anomaly_info and random.random() < 0.5:
            dmg = anomaly_info[1]['damage']
            rad = anomaly_info[1]['radiation']
            if dmg > 0:
                print(f"You are hit by the anomaly! Damage: {dmg}")
                game.player.take_damage(dmg)
            if rad > 0:
                print(f"You are irradiated by the anomaly! Radiation: {rad}")
                game.player.radiation += rad

def handle_mutant_encounter(game):
    if game.current_sector['mutant']:
        mutant_type = game.current_sector.get('mutant_type')
        from roguelike.world import MUTANT_TYPES, ITEM_POOL
        import random
        mutant_info = next((m for m in MUTANT_TYPES if m[0] == mutant_type), None)
        print(f"A mutant appears: {mutant_type}!")
        fight = input("Fight the mutant? (y/n): ")
        if fight.lower() == 'y':
            win_chance = 0.5 + game.player.get_attack_bonus()
            if random.random() < win_chance:
                print(f"You defeated the {mutant_type}!")
                loot_chance = 0.5
                loot_item = random.choice([i for i in ITEM_POOL if i])
                if random.random() < loot_chance:
                    game.player.add_item(loot_item)
                    print(f"You found loot on the mutant: {loot_item}!")
            else:
                dmg = mutant_info[1] if mutant_info else 15
                print(f"The {mutant_type} attacks you! Damage: {dmg}")
                game.player.take_damage(dmg)
        else:
            print(f"You avoid the {mutant_type}, but it scratches you as you flee!")
            dmg = mutant_info[1]//2 if mutant_info else 5
            game.player.take_damage(dmg)

def handle_sector_actions(game):
    print("Actions: 1) Move 2) Use Medkit 3) Use Anti-rad 4) Equip Item 5) Unequip 6) Quit")
    action = input("Choose action: ")
    if action == '1':
        game.current_sector = game.world.generate_sector()
    elif action == '2':
        if game.player.use_item("Medkit"):
            game.player.heal(20)
            print("You used a Medkit and healed 20 HP.")
        else:
            print("No Medkit in inventory.")
    elif action == '3':
        if game.player.use_item("Anti-rad"):
            game.player.heal_radiation(15)
            print("You used Anti-rad and reduced radiation by 15.")
        else:
            print("No Anti-rad in inventory.")
    elif action == '4':
        item = input("Enter item name to equip: ")
        if game.player.equip_item(item):
            print(f"Equipped {item}.")
        else:
            print("Item not found or not equippable.")
    elif action == '5':
        slot = input("Unequip 'weapon' or 'armor'?: ")
        if game.player.unequip_item(slot):
            print(f"Unequipped {slot}.")
        else:
            print("Nothing to unequip in that slot.")
    elif action == '6':
        print("You leave the Zone...")
        return False
    else:
        print("Invalid action.")
    return True 