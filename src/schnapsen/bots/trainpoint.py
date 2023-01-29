
# imprts 
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine, SchnapsenTrickScorer, Marriage, Score
# from schnapsen.bots.pointbot import PointBot
from schnapsen.bots.ml_bot import MLDataBot, MLPlayingBot

import random
import pathlib

from typing import Optional

import click
from schnapsen.bots import MLDataBot, train_ML_model, MLPlayingBot, RandBot, RdeepBot, AlphaBetaBot

#from schnapsen.bots.alphabeta import AlphaBetaBot
from schnapsen.game import (Bot, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, Trump_Exchange)
from schnapsen.twenty_four_card_schnapsen import \
    TwentyFourSchnapsenGamePlayEngine

from schnapsen.bots.rdeep import RdeepBot


# the point bot that does not want to import 
#########################################################################################################################################

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

##################################################################################################################################################



def create_replay_memory_dataset() -> None:
    # define replay memory database creation parameters
    num_of_games: int = 10000
    replay_memory_dir: str = 'ML_replay_memories'
    replay_memory_filename: str = 'random_random_10k_games.txt'
    replay_memory_location = pathlib.Path(replay_memory_dir) / replay_memory_filename

    bot_1_behaviour: Bot = PointBot(298434)
    bot_2_behaviour: Bot = RandBot(55444)
    delete_existing_older_dataset = False

    # check if needed to delete any older versions of the dataset
    if delete_existing_older_dataset and replay_memory_location.exists():
        print(f"An existing dataset was found at location '{replay_memory_location}', which will be deleted as selected.")
        replay_memory_location.unlink()

    # in any case make sure the directory exists
    replay_memory_location.parent.mkdir(parents=True, exist_ok=True)

    # create new replay memory dataset, according to the behaviour of the provided bots and the provided random seed
    engine = SchnapsenGamePlayEngine()
    replay_memory_recording_bot_1 = MLDataBot(bot_1_behaviour, replay_memory_location=replay_memory_location)
    replay_memory_recording_bot_2 = MLDataBot(bot_2_behaviour, replay_memory_location=replay_memory_location)

    for i in range(1, num_of_games + 1):
        if i % 500 == 0:
            print(f"Progress: {i}/{num_of_games}")
        engine.play_game(replay_memory_recording_bot_1, replay_memory_recording_bot_2, random.Random(i))
    print(f"Replay memory dataset recorder for {num_of_games} games.\nDataset is stored at: {replay_memory_location}")


create_replay_memory_dataset()

