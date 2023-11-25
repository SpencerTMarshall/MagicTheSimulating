import Effects

def game(state: Effects.State, turn: int, ind: int) -> int:
    #print((ind*"\t")+"TURN " + str(turn))
    # LAND FOR TURN
    if state.land > 0:
        #print((ind*"\t")+"Attempting to play land for turn")
        lowest = -1
        for x in range(len(state.hd.cardList)):
            if "Land" in state.hd.cardList[x].types:
                #print((ind*"\t")+"Found land: " + str(state.hd.cardList[x]))
                temp = Effects.cpy(state)

                temp.land -= 1
                
                temp.st.addToTop(temp.hd.cardList[x])
                temp.hd.cardList = temp.hd.cardList[:x] + temp.hd.cardList[x+1:]

                #print((ind*"\t")+"SUBGAME")
                res = game(state.hd.cardList[x].effect(temp)[0], turn, ind+1)

                if lowest == -1 or res < lowest:
                    lowest = res
        if lowest != -1: 
            return lowest

    # CHECK IF TRON
    if turn >= 5 or checklands(state.bf):
        return turn

    # TAP ALL LANDS FOR MANA 
    #print((ind*"\t")+"TAPPING FOR MANA...")
    for card in state.bf.cardList:
        if "Land" in card.types and not card.tapped:
            state.mana[0] += card.produce[0]
            state.mana[1] += card.produce[1]
            card.tapped = True
    
    lowest = -1

    # GO THROUGH HAND FOR CARDS TO CAST
    for card in state.hd.cardList:
        if "Land" not in card.types and canpay(state.mana[0], state.mana[1], card.cost):
            #print((ind*"\t")+"ATTEMPTING TO CAST " + str(card))
            temp = Effects.cpy(state)

            temp.mana = pay(temp.mana, card.cost)

            i = state.hd.cardList.index(card)

            temp.hd.cardList = temp.hd.cardList[:i] + temp.hd.cardList[i+1:]

            temp.st.addToTop(card)

            ans = card.effect(temp)

            #print((ind*"\t")+"FOUND " + str(len(ans)) + " SUBGAMES")
            for a in ans:
                #print((ind*"\t")+"SUBGAME")
                tt = game(a, turn, ind+1)
                if lowest == -1 or tt < lowest:
                    lowest = tt

    # GO THROUGH BOARD FOR ABILITIES TO ACTIVATE
    for card in state.bf.cardList:
        if "Land" not in card.types and len(card.abilities) != 0:
            if canpay(state.mana[0], state.mana[1], card.abilities[0].cost):
                #print((ind*"\t")+"ATTEMPTING TO ACTIVATE " + str(card))
                temp = Effects.cpy(state)
                temp.mana = pay(temp.mana, card.abilities[0].cost)

                ans = card.abilities[0].effect(temp)

                #print((ind*"\t")+"FOUND " + str(len(ans)) + " SUBGAMES")
                for a in ans:
                    #print((ind*"\t")+"SUBGAME")
                    tt = game(a, turn, ind+1)
                    if lowest == -1 or tt < lowest:
                        lowest = tt

    if lowest != -1:
        return lowest

    # END OF TURN
    #print((ind*"\t")+"ENDING TURN")
    state.hd.addToTop(state.lb.takeFromTop())
    state.mana = [0,0]
    state.land = 1

    for card in state.bf.cardList:
        card.tapped = False
    
    return game(state, turn+1, ind)

def canpay(cmana: int, gmana: int, cost: [int, int]) -> bool:
    if gmana >= cost[1]:
        newmana = gmana - cost[1]

        if cmana + newmana >= cost[0]:
            return True
        
    return False

def pay(starting: [int, int], cost: [int, int]):
    if starting[1] >= cost[1]:
        newmana = starting[1] - cost[1]

        if starting[0] >= cost[0]:
            return [starting[0]-cost[0], newmana]
        elif starting[0] + newmana >= cost[0]:
            remaining = cost[0]-starting[0]

            newmana = newmana - remaining

            return [0,newmana]


def checklands(board: Effects.MagicSim.Battlefield) -> bool:
    tower = False
    mine = False
    plant = False

    for card in board.cardList:
        if card.name == "Urza's Tower":
            tower = True
        elif card.name == "Urza's Mine":
            mine = True
        elif card.name == "Urza's Power Plant":
            plant = True
    
    return tower and mine and plant

def drawseven(lib: Effects.MagicSim.Library) -> [[Effects.MagicSim.Card], [Effects.MagicSim.Card]]:
    lib.shuffle()

    return [lib.cardList[7:], lib.cardList[:7]]

if __name__ == '__main__':
    start_lib = Effects.MagicSim.Library([Effects.UrzasPowerPlant() for x in range(4)] + 
                                         [Effects.UrzasMine() for x in range(4)] + 
                                         [Effects.UrzasTower() for x in range(4)] +
                                         [Effects.Forest() for x in range(3)] + 
                                         [Effects.ColourlessLand() for x in range(3)] +
                                         [Effects.Uncastable() for x in range(22)] + 
                                         [Effects.ChromaticSphere() for x in range(4)] + 
                                         [Effects.CandyTrail() for x in range(4)] +
                                         [Effects.SylvanScrying() for x in range(3)] +
                                         [Effects.ExpeditionMap() for x in range(4)] +
                                         [Effects.AncientStirrings() for x in range(4)])

    x = drawseven(start_lib)
    initial_library = Effects.MagicSim.Library(x[0])
    initial_hand = Effects.MagicSim.Hand(x[1])
    initial_graveyard = Effects.MagicSim.Graveyard([])
    initial_battlefield = Effects.MagicSim.Battlefield([])
    initial_stack = Effects.MagicSim.Stack([])

    initial_state = Effects.State(initial_battlefield, initial_graveyard, initial_library, initial_hand, initial_stack, 1)

    print("final: " + str(game(initial_state, 1, 0)))
    print("starting hand: " + str([y.name for y in x[1]]))