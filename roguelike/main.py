from roguelike.game import Game

def main():
    print("Welcome to Chronicles of the Wasteland: Anomalous Ether!")
    print("1. Start New Expedition")
    print("2. Exit")
    # Placeholder for menu logic
    choice = input("Choose an option: ")
    if choice == '1':
        game = Game()
        game.run()
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main() 