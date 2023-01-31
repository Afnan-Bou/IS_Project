from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer
from schnapsen.deck import Card, Suit

"""PointBot"""
class PointBot(Bot):
   """This bot plays different game strategies based on the points accumulated
   throughout the game. If the bot has 0-33 points while the opponent has more
   than 33 points, it will play aggressively. In all other cases it will play
   passively."""

   def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
       """Return the move that will be played"""
	
       valid_moves: list[Move] = state.valid_moves()
       my_points = state.get_my_score().direct_points
       opponent_points = state.get_opponent_score().direct_points
       trump_suit = state.get_trump_suit()

       rng_move_list: list[Move] = []
       marriage_trump_moves: list[Move] = []
       high_rank_card_move: list[Move] = []
       low_rank_card_move: list[Move] = []
       Schnapsen_trick_scorer = SchnapsenTrickScorer().rank_to_points
       chosen_move: Move
      
       """Aggressive play"""
       if 0<= my_points < 33 and opponent_points > 33:
           for move in valid_moves:
               if leader_move is None:
                   if move.is_trump_exchange() or move.is_marriage():
                       marriage_trump_moves.append(move)
                   else:
                       move_cards: list[Card] = move.cards
                       if Schnapsen_trick_scorer(move_cards[0].rank) == 11 and move_cards[0].suit == trump_suit:
                           chosen_move = move
                           return chosen_move
                       elif Schnapsen_trick_scorer(move_cards[0].rank) >= 10 and move_cards[0].suit != trump_suit:
                           high_rank_card_move.append(move)
                       else:
                           rng_move_list.append(move)

               else:
                   opponent_lead_suit: list[Card] = leader_move.cards
                   move_cards: list[Card] = move.cards
                   if move_cards[0].suit == opponent_lead_suit[0].suit and Schnapsen_trick_scorer(move_cards[0].rank) > Schnapsen_trick_scorer(opponent_lead_suit[0].rank):
                       chosen_move = move
                   elif opponent_lead_suit[0].suit != trump_suit and move_cards[0].suit == trump_suit:
                       chosen_move = move 
                   else:
                       rng_move_list.append(move)

           if len(marriage_trump_moves) != 0:
               return marriage_trump_moves[0] 
           else:
               if len(high_rank_card_move) != 0:
                   return high_rank_card_move[0]
               else: 
                   return valid_moves[0]


           """Passive play"""
       else:
           valid_moves: list[Move] = state.valid_moves()
           for move in valid_moves:
               if leader_move is None:
                   if move.is_trump_exchange() or move.is_marriage():
                       marriage_trump_moves.append(move)
                   else:
                       move_cards: list[Card] = move.cards
                       if Schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit:
                           low_rank_card_move.append(move) 
               else:
                   move_cards: list[Card] = move.cards
                   if Schnapsen_trick_scorer(move_cards[0].rank) <= 4 and move_cards[0].suit != trump_suit:
                       low_rank_card_move.append(move)
           if len(low_rank_card_move) == 0:
               for move in valid_moves:
                   rng_move_list.append(move)
           else:
               if len(low_rank_card_move) > 1:
                   return low_rank_card_move[0]
               else:
                   return low_rank_card_move[0]
           if len(marriage_trump_moves) != 0:
               return marriage_trump_moves[0]
           else:
               return valid_moves[0]


"""RandBot"""
import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move

class RandBot(Bot):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(
        self,
        state: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        moves: list[Move] = state.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def __repr__(self) -> str:
        return f"RandBot(seed={self.seed})"


"""BullyBot"""
import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer, RegularMove
from schnapsen.deck import Card, Suit

class BullyBot(Bot):
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move], ) -> Move:
        # The bully bot only plays valid moves.
        # get all valid moves
        my_valid_moves = player_perspective.valid_moves()
        trump_suit_moves: list[Move] = []

        # get the trump suit
        trump_suit: Suit = player_perspective.get_trump_suit()

        # get all my valid moves that have the same suit with trump suit.
        for move in my_valid_moves:
            cards_of_move: list[Card] = move.cards
            # get 1st of the list of cards of this move (in case of multiple -> Marriage)
            card_of_move: Card = cards_of_move[0]

            if card_of_move.suit == trump_suit:
                trump_suit_moves.append(move)

        # If you have cards of the trump suit, play one of them at random
        if len(trump_suit_moves) > 0:
            #random_trump_suit_move = self.rng.choice(trump_suit_moves)
            #return random_trump_suit_move
            return trump_suit_moves[0]

        # Else, if you are the follower and you have cards of the same suit as the opponent, play one of these at random.
        if not player_perspective.am_i_leader():
            assert leader_move is not None
            leader_suit: Suit = leader_move.cards[0].suit
            leaders_suit_moves: list[Move] = []

            # get all my valid moves that have the same suit with leader suit.
            for move in my_valid_moves:
                cards_of_move = move.cards
                # get 1st of the list of cards of this move (in case of multiple -> Marriage)
                card_of_move = cards_of_move[0]

                if card_of_move.suit == leader_suit:
                    leaders_suit_moves.append(move)

            if len(leaders_suit_moves) > 0:
                #random_leader_suit_move = self.rng.choice(leaders_suit_moves)
                #return random_leader_suit_move
                return leaders_suit_moves[0]

        # Else, play one of your cards with the highest rank

        # get the list of cards in my hand
        my_hand_cards: list[Card] = player_perspective.get_hand().cards

        # create an instance object of a SchnapsenTrickScorer Class, that allows us to get the rank of Cards.
        schnapsen_trick_scorer = SchnapsenTrickScorer()
        # we set the highest rank to something negative, forcing it to change with the first comparison, since all scores are positive
        highest_card_score: int = -1
        card_with_highest_score: Optional[Card] = None
        for card in my_hand_cards:
            card_score = schnapsen_trick_scorer.rank_to_points(card.rank)
            if card_score > highest_card_score:
                highest_card_score = card_score
                card_with_highest_score = card

        # if our logic above was correct, this can never be None. We double check to make sure.
        assert card_with_highest_score is not None

        # We now create a move out of this card. Note that here we do not return a move from a call to valid_moves.
        # An alternative implementaiton would first have taken all valid moves and subsequently filtered these down to
        # the list of valid cards. Then, we would have found the one with the highest score from that.
        move_of_card_with_highest_score = RegularMove(card_with_highest_score)

        # We can double check that this is a valid move like this.
        assert move_of_card_with_highest_score in my_valid_moves

        return move_of_card_with_highest_score


"""RdeepBot"""
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine
from random import Random


class RdeepBot(Bot):
    def __init__(self, num_samples: int, depth: int, rand: Random) -> None:
        """
        Create a new rdeep bot.

        :param num_samples: how many samples to take per move
        :param depth: how deep to sample
        :param rand: the source of randomness for this Bot
        """
        assert num_samples >= 1, f"we cannot work with less than one sample, got {num_samples}"
        assert depth >= 1, f"it does not make sense to use a dept <1. got {depth}"
        self.__num_samples = num_samples
        self.__depth = depth
        self.__rand = rand

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        # get the list of valid moves, and shuffle it such
        # that we get a random move of the highest scoring
        # ones if there are multiple highest scoring moves.
        moves = state.valid_moves()
        self.__rand.shuffle(moves)

        best_score = float('-inf')
        best_move = None
        for move in moves:
            sum_of_scores = 0.0
            for _ in range(self.__num_samples):
                gamestate = state.make_assumption(leader_move=leader_move, rand=self.__rand)
                score = self.__evaluate(gamestate, state.get_engine(), leader_move, move)
                sum_of_scores += score
            average_score = sum_of_scores / self.__num_samples
            if average_score > best_score:
                best_score = average_score
                best_move = move
        assert best_move is not None
        return best_move

    def __evaluate(self, gamestate: GameState, engine: GamePlayEngine, leader_move: Optional[Move], my_move: Move) -> float:
        """
        Evaluates the value of the given state for the given player
        :param state: The state to evaluate
        :param player: The player for whom to evaluate this state (1 or 2)
        :return: A float representing the value of this state for the given player. The higher the value, the better the
                state is for the player.
        """
        me: Bot
        leader_bot: Bot
        follower_bot: Bot

        if leader_move:
            # we know what the other bot played
            leader_bot = FirstFixedMoveThenBaseBot(RandBot(rand=self.__rand), leader_move)
            # I am the follower
            me = follower_bot = FirstFixedMoveThenBaseBot(RandBot(rand=self.__rand), my_move)
        else:
            # I am the leader bot
            me = leader_bot = FirstFixedMoveThenBaseBot(RandBot(rand=self.__rand), my_move)
            # We assume the other bot just random
            follower_bot = RandBot(self.__rand)

        new_game_state, _ = engine.play_at_most_n_tricks(game_state=gamestate, new_leader=leader_bot, new_follower=follower_bot, n=self.__depth)

        if new_game_state.leader.implementation is me:
            my_score = new_game_state.leader.score.direct_points
            opponent_score = new_game_state.follower.score.direct_points
        else:
            my_score = new_game_state.follower.score.direct_points
            opponent_score = new_game_state.leader.score.direct_points

        heuristic = my_score / (my_score + opponent_score)
        return heuristic


class RandBot(Bot):

    def __init__(self, rand: Random) -> None:
        self.rand = rand

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        return self.rand.choice(state.valid_moves())


class FirstFixedMoveThenBaseBot(Bot):
    def __init__(self, base_bot: Bot, first_move: Move) -> None:
        self.first_move = first_move
        self.first_move_played = False
        self.base_bot = base_bot

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if not self.first_move_played:
            self.first_move_played = True
            return self.first_move
        return self.base_bot.get_move(state=state, leader_move=leader_move)


"""Functions to run the experiments"""
import random
from typing import Optional
import click
from schnapsen.bots import RandBot, RdeepBot, SchnapsenServer

from schnapsen.game import (Bot, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine)

@click.group()
def main() -> None:
    """Various Schnapsen Game Examples"""

#to run the game type: python src/schnapsen/bots/pointbot.py play-my-game
@main.command()
def play_my_game() -> None: 
    engine = SchnapsenGamePlayEngine()
    bot1 = PointBot()
    bot2 = RandBot(5555555)
    #bot2 = RdeepBot(num_samples=16, depth=4, rand=random.Random(5555555))
    #bot2 = BullyBot(555555)
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


"""Binomial Test"""
from scipy import stats

## Comparing two bots: PointBot wins 542 out of 1000 games, and RandBot only 458
k1 = 542 # number of wins of PointBot
N1 = 1000 # total number of games
p_value_rand = stats.binom_test(k1, N1, alternative='greater') 

## Comparing two bots: PointBot wins 586 out of 1000 games, and BullyBot only 414
k2 = 586 # number of wins of PointBot
N2 = 1000 # total number of games
p_value_bully = stats.binom_test(k2, N2, alternative='greater')

## Comparing two bots: PointBot wins 219 out of 1000 games, and RdeepBot 781
k3 = 219 # number of wins of PointBot
N3 = 1000 # total number of games
p_value_rdeep = stats.binom_test(k3, N3, alternative='less')

print(p_value_rand)
print(p_value_bully)
print(p_value_rdeep)