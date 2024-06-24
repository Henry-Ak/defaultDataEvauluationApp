import streamlit as st
import requests
import matplotlib.pyplot as plt
import random
import pandas as pd

# Function to fetch pokemon data
def get_pokemon_data(pokemon_number):
  url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_number}"
  response = requests.get(url)
  return response.json() if response.status_code == 200 else None

# Function to generate random pokemon data (for comparison graph)
def get_random_pokemon(num_pokemon):
    data = []
    for _ in range(num_pokemon):
        pokemon_number = str(random.randint(1, 1025))
        data.append(get_pokemon_data(pokemon_number))
    return data

# Function to display moves in a DataFrame
def display_moves(moves):
  data = []
  for move in moves:
    move_data = move['move']
    data.append({
      "Name": move_data['name'],
      "Type": move_data.get('type', {}).get('name', None),
      "Power": move_data.get('power', None),
      "Accuracy": move_data.get('accuracy', None),
    })
  df = pd.DataFrame(data)
  st.dataframe(df, width = 1000)

# Main app
st.set_page_config(
    page_title="Pokedex",
    layout="wide"
)

st.title("Pokedex with Streamlit!")
pokemon_number = st.number_input("Enter a Pokemon number:", min_value=1, max_value=1025)

# Fetch data based on user input
pokemon_data = get_pokemon_data(pokemon_number)

if pokemon_data:
    st.subheader(f"Pokemon: {pokemon_data['name'].capitalize()}")
    col1, col2 = st.columns(2)

    #st.image(pokemon_data['sprites']['front_default'], width=200)
    # Display front and back sprites
    sprites = pokemon_data['sprites']
    image_list = [sprites['front_default'], sprites.get('back_default', None)]
    if sprites.get('other', {}).get('official-artwork', []):
      official_artworks = sprites.get('other', {}).get('official-artwork', [])
    if isinstance(official_artworks, list):
      image_list.extend([artwork['front_default'] for artwork in official_artworks])

    current_image_index = 0

    # Create buttons for navigation
    col2, col3 = st.columns(2)
    if current_image_index > 0:  # Enable "Back" button when not on the first image
      if st.button("Back", key="back_button"):
        current_image_index -= 1
    if current_image_index < len(image_list) - 1:  # Enable "Next" button when not on the last image
      if st.button("Next", key="next_button"):
        current_image_index += 1

    col1.image(image_list[current_image_index], width=200)

    # Display details in a table with headers
    df = pd.DataFrame({
    "Stat": ["Name", "Height", "Weight"] + [stat.get("stat", {}).get("name").capitalize() for stat in pokemon_data["stats"]],
    "Value": [pokemon_data["name"], pokemon_data["height"], pokemon_data["weight"]] + [stat["base_stat"] for stat in pokemon_data["stats"]]
    })

    st.dataframe(df, width=1000)

    # Display details like type and abilities
    with col2:
      st.write(f"Type: {', '.join(data['type']['name'] for data in pokemon_data['types'])}")
      st.write(f"Abilities: {', '.join(ability['ability']['name'] for ability in pokemon_data['abilities'])}")

    # Display moves in a separate DataFrame
    st.subheader("Moves:")
    display_moves(pokemon_data['moves'])

    # Generate comparison data
    comparison_data = get_random_pokemon(5)

    # Prepare data for graph
    heights = [pokemon_data["height"]] + [data["height"] for data in comparison_data if data]
    weights = [pokemon_data["weight"]] + [data["weight"] for data in comparison_data if data]
    pokemon_names = [pokemon_data["name"]] + [data["name"] for data in comparison_data if data]

    # Create the Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create the scatter plot on the figure
    ax.scatter(pokemon_names, heights, label="Height", color="blue")
    ax.scatter(pokemon_names, weights, label="Weight", color="red")
    ax.set_xlabel("Pokemon")
    ax.set_ylabel("Value")
    ax.set_title(f"Comparison of {pokemon_data['name'].capitalize()} (Height & Weight)")
    ax.legend()

    # Display the plot using st.pyplot
    st.pyplot(fig)
else:
    st.warning("Pokemon not found!")