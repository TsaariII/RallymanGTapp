from game import Game

def main() -> None:
    track_name = input('Enter track name: ').strip()
    if not track_name:
        print('No track name provided. Exiting.')
        return
    game = Game(track_name)
    game.start()

if __name__ == '__main__':
    main()