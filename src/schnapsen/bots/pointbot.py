#imports: 
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine, SchnapsenTrickScorer, Marriage, Score
from schnapsen.deck import Card, Rank, Suit
from typing import List, cast
import random



class PointBot(Bot): 
    """This bot plays differnet moves based on the points accumulated throughout the game"""


    def __init__(self, rng: random.Random) -> None:
        #Taken from bullybot 
        self.rng = rng


    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """"""
        valid_moves: list[Move] = state.valid_moves
        my_points = state.get_my_score().direct_points
        opponent_points = state.get_opponent_score().direct_points

        rng_move_list: list[Move] = []

        chosen_move: Move

        #When both players have 0 points, the bot will play one of the ranom valid moves. Implementing a better strategy than playing a random move could confound with the tests, so a random move is chosen. 
        if my_points == 0 and opponent_points == 0: 
            for move in valid_moves: 
                rng_move_list.append(move)
            chosen_move = self.rng.choice(rng_move_list)


        if my_points == 0 and opponent_points > 0: 
            pass 
            if leader_move is not None: 
                pass
            
        if my_points < 33 and opponent_points > 33: 
            pass 


        

