#imports: 
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine, SchnapsenTrickScorer, Marriage, Score
from schnapsen.deck import Card, Rank, Suit
import random

class PointBot(Bot): 
    """This bot plays different game strategies based on the points accumulated 
    throughout the game. If the bot has 0-33 points while the opponent has more 
    than 33 points, it will play aggressively. In all other cases it will play 
    passively."""

    def __init__(self, rng: random.Random) -> None:
        #Taken from bullybot 
        self.rng = rng
        

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """Return the move that will be played"""

        #Defining variables to store the valid moves that can be played, the number of points this bot has, the number of points the opponent has and the trump suit. 
        valid_moves: list[Move] = state.valid_moves()
        my_points = state.get_my_score().direct_points
        opponent_points = state.get_opponent_score().direct_points
        trump_suit = state.get_trump_suit()

        #Lists that will contain moves that can be played 
        rng_move_list: list[Move] = [] 
        marriage_trump_moves: list[Move] = []
        high_rank_card_move: list[Move] = []
        low_rank_card_move: list[Move] = []

        #To obtain the rank of a card: 
        schnapsen_trick_scorer = SchnapsenTrickScorer().rank_to_points
       
        #I didn't actually use these two lists but maybe we should incorporate them? ill just leave them here for now. 
        trump_moves: list[Move] = []
        same_suit_follower_moves: list[Move] = []
        
        chosen_move: Move 
        

        """Aggressive play"""
        if 0<= my_points < 33 and opponent_points > 33: 
            #play aggressively 
           
            for move in valid_moves: 
            #lead with a marriage, a high ranking trump, or an ace or ten at random
                if leader_move is None:
                    if move.is_trump_exchange() or move.is_marriage(): 
                        marriage_trump_moves.append(move)
                    else: 
                        move_cards: list[Card] = move.cards
                        if schnapsen_trick_scorer(move_cards[0].rank) == 11 and move_cards[0].suit == trump_suit: 
                            chosen_move = move #if you have the ace of trumps, play it. It will guarantee winning a trick.
                            return chosen_move 
                        elif schnapsen_trick_scorer(move_cards[0].rank) >= 10 and move_cards[0].suit != trump_suit: 
                            high_rank_card_move.append(move) #play a 10 or an ace of a non-trump suit if you have one. 
                        else: 
                            rng_move_list.append(move) #if the previous options are not possible, a move from this list will be selected randomly.

                #follow with a card that beats the opponent's card, if possible, by following suit with a higher ranking card, or play a trump to win the trick (if the leading card is not of the trump suit)
                else: 
                    opponent_lead_suit: list[Card] = leader_move.cards
                    move_cards: list[Card] = move.cards

                    if move_cards[0].suit == opponent_lead_suit[0].suit and schnapsen_trick_scorer(move_cards[0].rank) > schnapsen_trick_scorer(opponent_lead_suit[0].rank):
                        chosen_move = move #play a higher ranking card of the same suit 
                    elif opponent_lead_suit[0].suit != trump_suit and move_cards[0].suit == trump_suit: 
                        chosen_move = move #play a trump if the opponent leads with a non-trump card
                    else: 
                        rng_move_list.append(move) #if the other options are not possible, a random move from this list will be played.
                    
            #the following code will only be executed if 'chosen_move' is not returned (if the bot does not have a trump ace in its hand)
            #this is why the chosen_move variable is not part of the conditions below. 

            if len(marriage_trump_moves) != 0: 
                return marriage_trump_moves[0] #if possible, play a marriage or trump exchange
            else: 
                if len(high_rank_card_move) != 0:
                    #return self.rng.choice(list(high_rank_card_move)) #play a random high ranking card from the list 
                    return high_rank_card_move[0]
                else:  
                    #return self.rng.choice(list(rng_move_list))  #if there are no high rank card moves that can be played, play a random valid move
                    #return rng_move_list[0] 
                    return valid_moves[0]
 
            """Passive play"""
        else: 
            valid_moves: list[Move] = state.valid_moves()
            for move in valid_moves:
                #if leading, lead by announcing a marriage if possible, or lead with a low ranking, non-trump card 
                if leader_move is None: 
                    if move.is_trump_exchange() or move.is_marriage(): 
                        marriage_trump_moves.append(move)
                    else: 
                        move_cards: list[Card] = move.cards
                        if schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit: 
                            low_rank_card_move.append(move) #create a list of low ranking, non trump suit moves which can be played at random
                
                #if following, play a low ranking, non-trump card 
                else: 
                    move_cards: list[Card] = move.cards
                    if schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit: 
                        low_rank_card_move.append(move) 
            
            #if no low ranking, non-trump move is possible, the bot will play any of the valid moves at random
            if len(low_rank_card_move) == 0: 
                for move in valid_moves: 
                    rng_move_list.append(move)
            else: 
                if len(low_rank_card_move) > 1: 
                    #return self.rng.choice(list(low_rank_card_move)) #if there are low ranking moves possible, return one of them at random
                    return low_rank_card_move[0]
                else: 
                    return low_rank_card_move[0]

            #If a trump exchange or marriage is not possible (no moves added to marriage_trump_moves) then the bot will play a random move
            if len(marriage_trump_moves) != 0: 
                return marriage_trump_moves[0]
            else: 
                #return self.rng.choice(list(rng_move_list))
                #return rng_move_list[0]
                return valid_moves[0]


"""Im gonna try to run the cli.py game in this """
import random
import pathlib
from typing import Optional
import click
from schnapsen.bots import MLDataBot, train_ML_model, MLPlayingBot, RandBot, RdeepBot, AlphaBetaBot, SchnapsenServer

#from schnapsen.bots.alphabeta import AlphaBetaBot
#from schnapsen.bots.pointbot import PointBot

from schnapsen.game import (Bot, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, Trump_Exchange)
from schnapsen.twenty_four_card_schnapsen import \
    TwentyFourSchnapsenGamePlayEngine

from schnapsen.bots.rdeep import RdeepBot


@click.group()
def main() -> None:
    """Various Schnapsen Game Examples"""

#to run the game type: python src/schnapsen/bots/pointbot.py play-my-game
@main.command()
def play_my_game() -> None: 
    engine = SchnapsenGamePlayEngine()
    model_dir: str = 'ML_models'
    model_name: str = 'simple_model'
    model_location0 = pathlib.Path(model_dir) / model_name
    bot1 = PointBot(44)
    bot2 = RandBot(3)
    #bot2 = RdeepBot(num_samples=16, depth=4, rand=random.Random(4564654644))
    #bot2 = MLPlayingBot(model_location=model_location0)

    bot1_wins = 0 
    bot2_wins = 0
    points_won_1 = 0 #number of times our bot lost against the opponent and lost 1 point
    points_won_2 = 0
    points_won_3 = 0
    lead, follower = bot1, bot2
    for i in range(1000):
        if i % 2 == 0:
            # swap bots so both start the same number of times
            lead, follower = follower, lead
    for i in range(1000): 
        winner, points, score = engine.play_game(lead, follower, random.Random(i))  #the i in brackets allows different games to be played 
        
        if winner != bot2: 
            bot1_wins += 1 
        if winner == bot2: 
            bot2_wins += 1
            
            if points == 1: 
                points_won_1 += 1
            if points == 2: 
                points_won_2 += 1 
            if points == 3:
                points_won_3 += 1 
            
       #print(f"Winner is: {winner}, card score was {score} and  {points} gamepoints!") #these two lines are copied from exercise answers 

    print(f'{bot1} won {bot1_wins} times out of 1000. {bot2} won {bot2_wins} out of 1000, it scored 1 game point {points_won_1} times, 2 game points {points_won_2}, 3 game points {points_won_3}')

"""
if __name__ == "__main__":
    engine = SchnapsenGamePlayEngine()
    with SchnapsenServer() as s:
        bot1 = PointBot(13)
        bot2 = s.make_gui_bot(name="mybot2")
        # bot1 = s.make_gui_bot(name="mybot1")
        engine.play_game(bot1, bot2, random.Random(101))
"""

"""Function to store the data (we might need to change it up a bit)"""
@main.command() 
def play_games_and_return_stats(engine: SchnapsenGamePlayEngine, bot1: Bot, bot2: Bot, number_of_games: int) -> int:
    """
    Play number_of_games games between bot1 and bot2, using the SchnapsenGamePlayEngine, and return how often bot1 won.
    Prints progress.
    """
    bot1_wins: int = 0
    bot2_wins: int = 0 
    points_won_1: int = 0 
    points_won_2: int = 0 
    points_won_3: int = 0 

    lead, follower = bot1, bot2
    for i in range(1, number_of_games + 1):
        if i % 2 == 0:
            # swap bots so both start the same number of times
            lead, follower = follower, lead
        winner, points, score = engine.play_game(lead, follower, random.Random(i))
        if winner != bot2: 
            bot1_wins += 1 
        if winner == bot2: 
            bot2_wins += 1
            
            if points == 1: 
                points_won_1 += 1
            if points == 2: 
                points_won_2 += 1 
            if points == 3:
                points_won_3 += 1 
        #if i % 500 == 0:
            #print(f"Progress: {i}/{number_of_games}")
    print(f'{bot1} won {bot1_wins} times out of 1000. {bot2} won {bot2_wins} out of 1000, it scored 1 game point {points_won_1} times, 2 game points {points_won_2}, 3 game points {points_won_3}')

#play_games_and_return_stats(SchnapsenGamePlayEngine, PointBot, RandBot, 1000)

@main.group()
def ml() -> None:
    """Commands for the ML bot"""

@ml.command()  #to run this command: python src/schnapsen/bots/pointbot.py ml try-bot-game
def try_bot_game() -> None:
    engine = SchnapsenGamePlayEngine()
    model_dir: str = 'ML_models'
    model_name: str = 'simple_model'
    model_location = pathlib.Path(model_dir) / model_name
    bot1: Bot = PointBot(44)
    #bot2: Bot = RandBot(464566)
    bot2: Bot = MLPlayingBot(model_location)
    number_of_games: int = 1000

    # play games with altering leader position on first rounds
    ml_bot_wins_against_random = play_games_and_return_stats(engine=engine, bot1=bot1, bot2=bot2, number_of_games=number_of_games)
    print(f"The ML bot with name {model_name}, won {ml_bot_wins_against_random} times out of {number_of_games} games played.")



if __name__ == "__main__":
    main()


# this is for the two-tailed binomial test 

from scipy import stats

## Comparing two bots: PointBot wins 663 out of 1000 games, and RandBot only 337
k1 = 663 # number of wins of PointBot
N1 = 1000 # total number of games
p_value_rand = stats.binom_test(k1, N1, alternative='two-sided')

## Comparing two bots: PointBot wins 619 out of 1000 games, and BullyBot only 381
k2 = 619 # number of wins of PointBot
N2 = 1000 # total number of games
p_value_bully = stats.binom_test(k2, N2, alternative='two-sided')

## Comparing two bots: PointBot wins 252 out of 1000 games, and RdeepBot 748
k3 = 252 # number of wins of PointBot
N3 = 1000 # total number of games
p_value_rdeep = stats.binom_test(k3, N3, alternative='two-sided')

print(p_value_rand)
print(p_value_bully)
print(p_value_rdeep)