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

        trump_suit = state.get_trump_suit()

        rng_move_list: list[Move] = []

        marriage_trump_moves: list[Move] = []

        #to obtain the rank of a card: 
        schnapsen_trick_scorer = SchnapsenTrickScorer().rank_to_points
       

        trump_moves: list[Move] = []
        same_suit_follower_moves: list[Move] = []
        chosen_move: Move

        #When both players have 0 points, the bot will play one of the random valid moves. 
        #Implementing a better strategy than playing a random move could confound with the tests, so a random move is chosen. 
        #If this bot is leading it will also try to play either a trump exchange or a marriage 
        if my_points == 0 and 0 <= opponent_points < 33: 
            #plays passively: a low ranking card 

            for move in valid_moves:
                #lead by announcing a marriage if possible, or lead with a low ranking, non-trump card 
                if leader_move is None: 
                    if move.is_trump_exchange() or move.is_marriage(): 
                        marriage_trump_moves.append(move)
                    else: 
                        move_cards: list[Card] = move.cards
                        if schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit: 
                            rng_move_list.append(move) 
                
                #if following, play a low ranking, non-trump card 
                else: 
                    move_cards: list[Card] = move.cards
                    if schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit: 
                        rng_move_list.append(move) 
            
            #if no low ranking move is possible, the bot will play any of the valid moves at random
            if len(rng_move_list) == 0: 
                for move in valid_moves: 
                    rng_move_list.append(move)

            #If a trump exchange or marriage is not possible (no moves added to marriage_trump_moves) then the bot will play a random move
            if len(marriage_trump_moves) != 0: 
                return marriage_trump_moves[0]
            else: 
                return self.rng.choice(rng_move_list)
        
        if 0 <= my_points < 33 and opponent_points > 33: 
            #Play aggressively 
            pass 

        if my_points > 33 and opponent_points > 33: 
            #play passively 
            for move in valid_moves: 
                if not move.is_marriage(): 
                    pass
                #play in a way to ensure that you win the last trick.
            #if neither you or the opponent have played a marriage: 
            # then try to play out the last tricks in such a way that you win the last trick, so that you win the game even without reaching 66 points 


                #if not 
       # else: 
           # for move in valid_moves: 
             #   rng_move_list.append(move)
            #chosen_move = self.rng.choice(rng_move_list)

        else: 
            return valid_moves #play any move 

