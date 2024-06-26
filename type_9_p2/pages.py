from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants

class Instructions(Page):

    def is_displayed(self):
        P = self.subsession.get_players()[0]       
        return (P.participant.vars['p2_cycle'] == 1) & (P.participant.vars['p2_round'] == 0)

class Update(WaitPage):

    wait_for_all_groups = True

    # ASSIGN GROUPS
    # UPDATE ROUND VARIABLES
    # GIVEN CONDITIONS:
    #     GENERATE A NEW CYCLE
    # PRINT
    
    def is_displayed(self):
        P = self.subsession.get_players()[0]
        cycle = P.participant.vars['p2_cycle']
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']]+[0])
        return (cycle <= Constants.Cycle_Condition_3)

    def after_all_players_arrive(self):

        for p in self.subsession.get_players():                                                                 # Update Variables This Round
            p.new_round() 

        P = self.subsession.get_players()[0]                                                                    # REPRESENTATIVE PLAYER
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']-1]+[0])  # Maximum Die Roll This Cycle
        if max_roll > Constants.Cycle_Condition_1:                                                              # Given Cycle Conditions
            for p in self.subsession.get_players():                                                             # Generate New Cycle
                p.new_cycle()
                
        groups_by_cycle = Constants.groups_by_cycle_dict[len(self.session.get_participants())]
        groups = groups_by_cycle[self.session.get_participants()[0].vars['p2_cycle']-1]
        self.subsession.set_group_matrix(groups)

        print(' ')
        print('Round Number: ',P.round_number)
        print(' Round: ',P.p2_round)
        print(' Cycle: ',P.p2_cycle)

class Decision(Page):

    form_model = 'player'
    form_fields = ['decision']
    
    def is_displayed(self):
        P = self.subsession.get_players()[0]
        cycle = P.participant.vars['p2_cycle']
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']-1]+[0])
        return (cycle <= Constants.Cycle_Condition_3) & (max_roll <= Constants.Cycle_Condition_1)
    
    def vars_for_template(self):
        round_number = self.player.p2_round
        player_in_all_rounds = self.player.in_all_rounds()[-round_number:-1]
        player_in_all_rounds = player_in_all_rounds[::-1]
        opponent_in_all_rounds = self.player.get_others_in_group()[0].in_all_rounds()[-round_number:-1]
        cycle = self.player.p2_cycle
        
        return {'player_in_all_rounds': player_in_all_rounds,
                'opponent_in_all_rounds': opponent_in_all_rounds,
                'cycle':cycle,
                'round':round_number}

class ResultsWaitPage(WaitPage):
    
    def is_displayed(self):
        P = self.subsession.get_players()[0]
        cycle = P.participant.vars['p2_cycle']
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']-1]+[0])
        return (cycle <= Constants.Cycle_Condition_3) & (max_roll <= Constants.Cycle_Condition_1)

    def after_all_players_arrive(self):

        def group_decision_function(X):
            for x in X:
                if x == 'Green':
                    return 'Any of 3 Green'
            return 'All 3 Red'
        
        for P in self.group.get_players():
            group_member_decisions = [p.decision for p in P.get_others_in_group()]
            P.group_decision = group_decision_function(group_member_decisions)
            P.set_payoff()
            
class Results(Page):

    def is_displayed(self):
        P = self.subsession.get_players()[0]
        cycle = P.participant.vars['p2_cycle']
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']-1]+[0])
        return (cycle <= Constants.Cycle_Condition_3) & (max_roll <= Constants.Cycle_Condition_1)

    def vars_for_template(self):
        round_number = self.player.p2_round
        player_in_all_rounds = self.player.in_all_rounds()[-round_number:]
        opponent_in_all_rounds = self.player.get_others_in_group()[0].in_all_rounds()[-round_number:]
        player_in_all_rounds = player_in_all_rounds[::-1]
        player_decision = self.player.decision
        group_decision = self.player.group_decision
        die_roll = self.player.die_roll
        cycle = self.player.p2_cycle
        
        def bin_own(x):
            if x == 'Green':
                return 1
            if x == 'Red':
                return 2
            
        def bin_other(x):
            if x == 'Any of 3 Green':
                return 1
            if x == 'All 3 Red':
                return 2
        
        return {'player_in_all_rounds': player_in_all_rounds,
                'opponent_in_all_rounds': opponent_in_all_rounds,
                'player_decision':player_decision,
                'cycle':cycle,
                'round':round_number,
                'die_roll':die_roll,
                'bin_own':bin_own(str(player_decision)),
                'bin_other':bin_other(str(group_decision)),
                'cycle_condition_2': Constants.Cycle_Condition_2,
               }

class Summary(Page):

    def is_displayed(self):
        P = self.subsession.get_players()[0]
        max_roll = max(Constants.die[P.participant.vars['p2_cycle']-1][:P.participant.vars['p2_round']]+[0])
        reveal_round = P.participant.vars['p2_round']
        cycle = P.participant.vars['p2_cycle']
        return (cycle <= Constants.Cycle_Condition_3) & (max_roll > Constants.Cycle_Condition_1)

    def vars_for_template(self):
        round_number = self.player.p2_round
        player_in_all_rounds = self.player.in_all_rounds()[-round_number:]
        player_in_all_rounds = player_in_all_rounds[::-1]
        opponent_in_all_rounds = self.player.get_others_in_group()[0].in_all_rounds()[-round_number:]
        player_decision = self.player.decision
        group_decision = self.player.group_decision
        die_roll = self.player.die_roll
        cycle = self.player.p2_cycle
        payoff = self.player.payoff
        
        self.participant.vars['p2_payment'].append(payoff)
        self.participant.vars['p2_payment_round'].append(round_number)
        
        return {'player_in_all_rounds': player_in_all_rounds,
                'opponent_in_all_rounds': opponent_in_all_rounds,
                'player_decision':player_decision,
                'group_decision':group_decision,
                'cycle':cycle,
                'round':round_number,
                'die_roll':die_roll,
                'payoff':payoff}    

page_sequence = [
    Instructions,
    Update,
    Decision,
    ResultsWaitPage,
    Results,
    Summary,
]
