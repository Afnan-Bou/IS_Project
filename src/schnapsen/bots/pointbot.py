#imports: 
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine, SchnapsenTrickScorer, Marriage, Score
from schnapsen.deck import Card, Rank, Suit
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
        

        """Idea to change the code to just be two states since the bot only plays aggressively for one conditon and passively for all others"""
        if 0<= my_points < 33 and opponent_points > 33: 
            #play aggressively 
           
            for move in valid_moves: 
            #lead with a marriage, or a high ranking trump or an ace or ten at random
                if leader_move is None:
                    if move.is_trump_exchange() or move.is_marriage(): 
                        marriage_trump_moves.append(move)
                    else: 
                        move_cards: list[Card] = move.cards
                        if schnapsen_trick_scorer(move_cards[0].rank) == 11 and move_cards[0].suit == trump_suit: 
                            chosen_move == move 
                        elif schnapsen_trick_scorer(move_cards[0].rank) >= 10 and move_cards[0].suit != trump_suit: 
                            rng_move_list.append(move)

                #follow with a card that beats the opponent's card, if possible 
                #follow suit with a card of higher rank 
                else: 
                    opponent_lead_suit: list[Card] = leader_move.cards
                    move_cards: list[Card] = move.cards

                    if move_cards[0].suit == opponent_lead_suit[0].suit and schnapsen_trick_scorer(move_cards[0].rank) > schnapsen_trick_scorer(opponent_lead_suit[0].rank):
                        chosen_move = move #play a higher ranking card of the same suit 
                    elif opponent_lead_suit[0].suit != trump_suit and move_cards[0].suit == trump_suit: 
                        chosen_move = move #play a trump if the opponent leads with a non-trump card
                    else: 
                        rng_move_list.append(move)
                    
            #return the marriage or trump move if one exists, return the defined chosen_move variable if possible or play a random move.
            if len(marriage_trump_moves) != 0: 
                return marriage_trump_moves[0]
            else: 
                if len(rng_move_list) == 0: 
                    return chosen_move
                else:  
                    return self.rng.choice(rng_move_list)

            """For all other states: passive gameplay"""
        else: 
            #play passively (all the other states we mentioned involved playing passively and since the code is all the same we can just combine the states into one)
            
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
            
            #if no low ranking, non-trump move is possible, the bot will play any of the valid moves at random
            if len(rng_move_list) == 0: 
                for move in valid_moves: 
                    rng_move_list.append(move)

            #If a trump exchange or marriage is not possible (no moves added to marriage_trump_moves) then the bot will play a random move
            if len(marriage_trump_moves) != 0: 
                return marriage_trump_moves[0]
            else: 
                return self.rng.choice(rng_move_list)


