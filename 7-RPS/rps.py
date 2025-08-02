import random
import time
from collections import defaultdict

# Rock, Paper, Scissors with AI Learning
# Inspired by the University of Stirling's RPS game: https://www.cs.stir.ac.uk/~kms/schools/rps/index.php
# The AI uses conditional probabilities to learn player patterns and predict their next move

class RPSGame:
    def __init__(self):
        self.moves = ['rock', 'paper', 'scissors']
        self.beats = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        self.player_score = 0
        self.ai_score = 0
        self.game_history = []
        self.player_history = []
        
        # AI learning parameters
        self.conditional_probs = defaultdict(lambda: {'rock': 0.33, 'paper': 0.33, 'scissors': 0.33})
        self.last_player_move = None
        
    def get_ai_move(self):
        """AI chooses move based on learned patterns"""
        if not self.player_history:
            # If no history, choose randomly
            return random.choice(self.moves)
        
        # Get conditional probabilities based on last player move
        last_move = self.player_history[-1]
        probs = self.conditional_probs[last_move]
        
        # Find the move the player is most likely to choose
        most_likely_move = max(probs, key=probs.get)
        
        # Choose the move that beats the most likely player move
        ai_move = self.beats[most_likely_move]
        
        return ai_move
    
    def update_ai_learning(self, player_move):
        """Update AI's learning based on player's move"""
        if self.last_player_move is not None:
            # Update conditional probabilities
            total_moves = sum(self.conditional_probs[self.last_player_move].values())
            
            # Increment the count for the current move
            self.conditional_probs[self.last_player_move][player_move] += 1
            
            # Normalize probabilities
            new_total = sum(self.conditional_probs[self.last_player_move].values())
            for move in self.moves:
                self.conditional_probs[self.last_player_move][move] = (
                    self.conditional_probs[self.last_player_move][move] / new_total
                )
        
        self.last_player_move = player_move
    
    def determine_winner(self, player_move, ai_move):
        """Determine the winner of the round"""
        if player_move == ai_move:
            return "tie"
        elif self.beats[player_move] == ai_move:
            return "ai"
        else:
            return "player"
    
    def display_rules(self):
        """Display game rules"""
        print("\n" + "="*50)
        print("ROCK, PAPER, SCISSORS - AI LEARNING GAME")
        print("="*50)
        print("Rules:")
        print("• Paper wraps (beats) Rock")
        print("• Scissors cut (beat) Paper") 
        print("• Rock blunts (beats) Scissors")
        print("\nThe AI learns your patterns and tries to beat you!")
        print("Try these strategies to test the AI:")
        print("1. Pick Rock, Paper, Scissors in a repeating pattern")
        print("2. Pick the same move multiple times in a row")
        print("3. Try to be completely random")
        print("="*50)
    
    def get_player_move(self):
        """Get player's move with input validation"""
        while True:
            print(f"\nYour move: rock (r), paper (p), scissors (s)")
            # Set to true to play against the ai
            play_against_ai = True
            if play_against_ai:
                player_input = input("Enter your choice: ").lower().strip()
            else:
                random_move = random.choice(self.moves)
                player_input = random_move
            
            if player_input in self.moves:
                return player_input
            elif player_input in ['r', 'rock']:
                return 'rock'
            elif player_input in ['p', 'paper']:
                return 'paper'
            elif player_input in ['s', 'scissors']:
                return 'scissors'
            elif player_input in ['quit', 'exit', 'q']:
                return 'quit'
            else:
                print("Invalid choice! Please enter r, p, s, or the full word.")
    
    def display_round_result(self, player_move, ai_move, result):
        """Display the result of a round"""
        print(f"\nYou chose: {player_move.upper()}")
        print(f"AI chose: {ai_move.upper()}")
        
        if result == "tie":
            print("It's a tie!")
        elif result == "player":
            print("You win!")
            self.player_score += 1
        else:
            print("AI wins!")
            self.ai_score += 1
        
        print(f"Score - You: {self.player_score}, AI: {self.ai_score}")
    
    def display_ai_learning(self):
        """Display AI's current learning state"""
        if not self.player_history:
            return
        
        print("\n" + "-"*30)
        print("AI LEARNING STATUS:")
        print("-"*30)
        
        for last_move in self.moves:
            if last_move in self.conditional_probs:
                probs = self.conditional_probs[last_move]
                print(f"After you played {last_move.upper()}:")
                for move, prob in probs.items():
                    print(f"  {move.upper()}: {prob:.2%}")
                print()
    
    def play_game(self):
        """Main game loop"""
        self.display_rules()
        
        print("\nLet's play! Type 'quit' to exit.")
        
        while True:
            # Get player move
            player_move = self.get_player_move()
            
            if player_move == 'quit':
                break
            
            # Get AI move
            ai_move = self.get_ai_move()
            
            # Determine winner
            result = self.determine_winner(player_move, ai_move)
            
            # Display result
            self.display_round_result(player_move, ai_move, result)
            
            # Update game history
            self.game_history.append((player_move, ai_move, result))
            self.player_history.append(player_move)
            
            # Update AI learning
            self.update_ai_learning(player_move)
            
            # Show AI learning status every 5 rounds
            if len(self.game_history) % 5 == 0:
                self.display_ai_learning()
            
            # Small delay for better UX
            time.sleep(0.5)
        
        # Game over
        print(f"\nFinal Score - You: {self.player_score}, AI: {self.ai_score}")
        if self.player_score > self.ai_score:
            print("Congratulations! You won the game!")
        elif self.ai_score > self.player_score:
            print("The AI won! Better luck next time!")
        else:
            print("It's a tie!")
        
        print(f"\nTotal rounds played: {len(self.game_history)}")
        print("Thanks for playing!")

def main():
    """Main function to start the game"""
    print("Welcome to Rock, Paper, Scissors with AI Learning!")
    
    game = RPSGame()
    game.play_game()

if __name__ == "__main__":
    main()
