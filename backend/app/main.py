from game import Game
from db_init import init_tracks_db

def main() -> None:
    track_name = input('Enter track name: ').strip()
    if not track_name:
        print('No track name provided. Exiting.')
        return
    init_tracks_db()
    game = Game(track_name)
    game.start()

if __name__ == '__main__':
    main()