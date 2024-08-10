https://youtu.be/H-E8dfufwHQ?si=dV63oQeysqwwdZjG

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/H-E8dfufwHQ/0.jpg)](https://www.youtube.com/watch?v=H-E8dfufwHQ)

Transcript generated with ChatGPT

## Banana Mesh: Finite State Machine for TouchDesigner

Today, I’m showcasing another component I've been working with extensively, the **Banana Mesh**. The name is a playful take on "meshed banana," but what exactly is Banana Mesh? It’s a finite state machine (FSM) for TouchDesigner.

### What is a Finite State Machine?

An FSM is a closed system with a defined set of states, such as `init`, `ADC`, and `momentary`. States have durations and conditions for transitions. Configuring these transitions enables you to create self-contained, stable systems ideal for permanent installations where manual intervention isn't feasible.

### Parameters and Setup

1. **State Information:**
   - **Mode:** Indicates whether it's a state or a transition.
   - **Current State and Transition:** Shows the active state and the state it’s transitioning to.
   - **Transition Fraction:** Normalized value (0 to 1) representing transition progress.

2. **Settings Page:**
   - **Init State:** Defines the entry state on startup or restart.
   - **Check on Parameter Change:** Reacts to changes in custom parameters.
   - **Check Mode:** Can be per parameter or end of frame.
   - **Check on State Time:** Transitions based on state duration.
   - **Check on State Enter:** Re-evaluates conditions when entering a state.
   - **Enforce Minimum Transition Time:** Ensures a transition time of at least one frame to prevent endless loops.

3. **Callbacks:**
   - React to state changes using Python.
   - Define custom callbacks for specific state transitions.

### UI Overview

- **State Selection:** Click on a state to select it, indicated by a yellow border.
- **Connections:** Displayed as arrows between states; clicking an arrow selects the connection.
- **Creating States and Connections:** Double-click to create a new state, right-click and drag to create connections.
- **Adjusting Parameters:** Set duration, transition times, and parameter filters for transitions.

### Example: Interactive Installation

I created a prototype for an interactive installation with states: `init`, `idle`, `interactive`, `enough`, and `goodbye`. Here’s a brief rundown:

1. **Init State:** Transitions immediately to idle.
2. **Idle State:** Displays a "come closer" message.
3. **Interactive State:** Activates upon player detection using a face tracker.
4. **Enough State:** Activates after 30 seconds of interaction, prompting users to allow others a turn.
5. **Goodbye State:** Displays a thank-you message before returning to idle.

Transitions are managed using parameters and conditions, ensuring a smooth flow between states.

### Advanced Use

Banana Mesh allows for extensive customization through Python logic, enabling complex conditions like file existence checks or specific time triggers. The system is efficient, minimizing resource usage even in complex projects.

### Conclusion

The Banana Mesh FSM component is highly versatile and stable, making it ideal for creating reliable installations. For more details or to contribute, visit my GitHub. Also, consider supporting through Patreon if you find these components useful in your projects.
