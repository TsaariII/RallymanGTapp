
import readline from 'readline';
import { Game } from './Game.ts';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question("Enter track name: ", (trackName) => {
  const game = new Game(trackName);
  game.start();
  rl.close();
});
