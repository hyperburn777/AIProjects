def state_weights(filename="state_weights.txt"):
    with open(filename, 'r') as f:
        lines = f.readlines()

    num_states = int(lines[1].split(' ')[0])
    state_weights = {}
    for line in lines[2:]:
        parts = line.split(' ')
        state = parts[0].strip('"\n')
        weight = int(parts[1])
        state_weights[state] = weight

    total = sum(state_weights.values())
    probs = {s: w / total for s, w in state_weights.items()}
    return probs, set(state_weights.keys())

def state_action_state_weights(states, filename="state_action_state_weights.txt"):
    with open(filename, 'r') as f:
        lines = f.readlines()

    num_triples, num_states, num_actions, default_weight = map(int, lines[1].split(' '))
    triples = {}
    actions = set()
    for line in lines[2:]:
        parts = line.split(' ')
        s, a, s_next, weight = parts[0].strip('"\n'), parts[1].strip('"\n'), parts[2].strip('"\n'), int(parts[3])

        # Init inner dict
        if (s, a) not in triples:
            triples[(s, a)] = {}
        triples[(s, a)][s_next] = weight
        actions.add(a)

    # Normalize
    trans = {}
    for s in states:
        for a in actions:
            # Init inner dict
            if (s, a) not in trans:
                trans[(s, a)] = {}
                
            next_states = triples.get((s, a), {})
            full_weights = {s_next: next_states.get(s_next, default_weight) for s_next in states}
            total = sum(full_weights.values())
            if total == 0: continue  # Avoid division by zero
            for s_next, weight in full_weights.items():
                trans[(s, a)][s_next] = weight / total

    return trans

def state_observation_weights(states, filename="state_observation_weights.txt"):
    with open(filename, 'r') as f:
        lines = f.readlines()

    num_pairs, num_states, num_observations, default_weight = map(int, lines[1].split(' '))
    pairs = {}
    observations = set()
    for line in lines[2:]:
        parts = line.split(' ')
        s, o, weight = parts[0].strip('"\n'), parts[1].strip('"\n'), int(parts[2])
        
        # Init inner dict
        if s not in pairs:
            pairs[s] = {}
        pairs[s][o] = weight
        observations.add(o)

    emit = {}
    for s in states:
        # Init inner dict
        if s not in emit:
            emit[s] = {}
            
        all_obs = set(pairs.get(s, {}).keys()).union(observations)
        full_weights = {o: pairs.get(s, {}).get(o, default_weight) for o in all_obs}
        total = sum(full_weights.values())
        if total == 0: continue  # Avoid division by zero
        for o, weight in full_weights.items():
            emit[s][o] = weight / total

    return emit

def observation_actions(filename="observation_actions.txt"):
    with open(filename, 'r') as f:
        lines = f.readlines()

    num_pairs = int(lines[1])
    pairs = []
    for line in lines[2:]:
        parts = line.split(' ')
        o, a = parts[0].strip('"\n'), parts[1].strip('"\n') if len(parts) >= 2 else None
        pairs.append((o, a))

    return pairs

def viterbi(init, trans, emit, obs_actions, states):
    T = len(obs_actions)
    prob = [{} for _ in range(T)]
    prev = [{} for _ in range(T)]
    
    # Initialization
    first_obs = obs_actions[0][0]
    for s in states:
        prob[0][s] = init.get(s, 0) * emit.get(s, {}).get(first_obs, 0)
    
    # Recursion
    for t in range(1, T):
        current_obs, current_action = obs_actions[t]
        
        for s in states:
            max_prob = 0
            best_prev = None
            
            for r in states:
                prev_action = obs_actions[t-1][1] if t > 0 else None # Use action from previous  step
                
                if prev_action is not None:
                    trans_prob = trans.get((r, prev_action), {}).get(s, 0)
                else:
                    trans_prob = 1 if s == r else 0  # No action means stay in same state
                
                new_prob = prob[t-1].get(r, 0) * trans_prob
                
                if new_prob > max_prob:
                    max_prob = new_prob
                    best_prev = r
            
            emit_prob = emit.get(s, {}).get(current_obs, 0)
            prob[t][s] = max_prob * emit_prob
            prev[t][s] = best_prev
        
    # Backtrace
    if not prob[-1]:
        return []
    
    print("---Final Probabilities---")
    for s, p in prob[-1].items():
        print(f"P({s}): {p}")

    best_last = max(prob[-1].items(), key=lambda x: x[1])[0]
    path = [best_last]
    for t in range(T-1, 0, -1):
        path.insert(0, prev[t][path[0]])
    
    return path

if __name__ == "__main__":
    init, states = state_weights()
    trans = state_action_state_weights(states)
    emit = state_observation_weights(states)
    obs = observation_actions()

    state_sequence = viterbi(init, trans, emit, obs, states)

    with open("states.txt", "w") as f:
        f.write("states\n")
        f.write(f"{len(state_sequence)}\n")
        for s in state_sequence:
            f.write(f'"{s}"\n')