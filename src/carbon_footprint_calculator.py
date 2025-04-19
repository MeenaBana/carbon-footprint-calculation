"""
Carbon Footprint Calculator for Meals

This script calculates the carbon footprint of meals based on food items
and their quantities, using data on the greenhouse gas emissions of various foods.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from tabulate import tabulate
import argparse

class CarbonFootprintCalculator:
    """
    A calculator for determining the carbon footprint of meals based on food items.
    """
    
    def __init__(self, data_file):
        """
        Initialize the calculator with the food production data.
        
        Args:
            data_file (str): Path to the CSV file with food production carbon footprint data
        """
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Food_Production.csv")

        try:
            self.cfp_data = pd.read_csv(data_file)
            self.process_data()
            print(f"Data loaded successfully from {data_file}")
        except FileNotFoundError:
            print(f"Error: The file {data_file} was not found.")
            print("Please download the dataset from: https://www.kaggle.com/selfvivek/environment-impact-of-food-production")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)
    
    def process_data(self):
        """Process and clean the carbon footprint data"""
        # Take only food product and total emissions columns
        self.cfp_food = self.cfp_data.loc[:, ['Food product', 'Total_emissions']]
        # Rename columns to more concise names
        self.cfp_food.columns = ['food', 'cfp']
        # Convert food item names to lowercase for easier matching
        self.cfp_food['food'] = self.cfp_food['food'].str.lower()
        # Sort by carbon footprint for better visualization
        self.cfp_food = self.cfp_food.sort_values(by='cfp')
        self.food_list = list(self.cfp_food['food'])
    
    def get_food_list(self):
        """Return the list of available food items"""
        return self.food_list
    
    def suggest_alternatives(self, food_item, max_suggestions=3):
        """
        Suggest lower carbon footprint alternatives for a given food item.
        
        Args:
            food_item (str): The food item to find alternatives for
            max_suggestions (int): Maximum number of alternatives to suggest
            
        Returns:
            list: List of suggested alternative food items with lower carbon footprints
        """
        if food_item not in self.food_list:
            return []
        
        item_cfp = self.cfp_food.loc[self.cfp_food['food'] == food_item, 'cfp'].values[0]
        
        alternatives_lower_cfp = self.cfp_food[self.cfp_food['cfp'] < item_cfp]
        
        if alternatives_lower_cfp.empty:
            return []
        
        return [(row['food'], row['cfp']) for _, row in alternatives_lower_cfp.sort_values(by='cfp', ascending=False).head(max_suggestions).iterrows()]
    
    def calculate_footprint(self, items):
        """
        Calculate the total carbon footprint for a list of food items and quantities.
        
        Args:
            items (list): List of (food_item, quantity) tuples
            
        Returns:
            float: Total carbon footprint in kg CO2 equivalents
            dict: Detailed breakdown of carbon footprint by food item
        """
        items_cfps = []
        item_breakdown = {}
        
        for item, quantity in items:
            if item not in self.food_list:
                print(f"Warning: {item} not found in the database. Skipping.")
                continue
            
            item_cfp = self.cfp_food.loc[self.cfp_food['food'] == item, 'cfp'].values[0]
            item_cfp_q = quantity * item_cfp
            items_cfps.append(item_cfp_q)
            
            item_breakdown[item] = {
                'quantity': quantity,
                'unit_cfp': item_cfp,
                'total_cfp': item_cfp_q
            }
        
        total_cfp = sum(items_cfps)
        
        return total_cfp, item_breakdown
    
    def plot_food_comparison(self, save_path=None):
        """
        Create a horizontal bar plot comparing carbon footprints of different foods.
        
        Args:
            save_path (str, optional): Path to save the figure. If None, the figure is displayed.
        """
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(folder_path, exist_ok=True)

        filename = "food_comparison.png"  
        save_path = os.path.join(folder_path, filename)

        plt.figure(figsize=(12, 15))
        
        sns.set_style("whitegrid")
        ax = sns.barplot(x='cfp', y='food', data=self.cfp_food, palette='viridis')
        
        plt.title('Carbon Footprint by Food Item (kg CO₂ per kg of food)', fontsize=16)
        plt.xlabel('Carbon Footprint (kg CO₂ equivalents)', fontsize=12)
        plt.ylabel('Food Item', fontsize=12)
       
        for i, v in enumerate(self.cfp_food['cfp']):
            ax.text(v + 0.5, i, f"{v:.1f}", va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Food comparison plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_meal_breakdown(self, meal_name, items, save_path=None):
        """
        Create a pie chart showing the carbon footprint breakdown of a meal.
        
        Args:
            meal_name (str): Name of the meal
            items (list): List of (food_item, quantity) tuples
            save_path (str, optional): Path to save the figure. If None, the figure is displayed.
        """
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(folder_path, exist_ok=True)

        filename = f"breakdown_{meal_name}.png"
        save_path = os.path.join(folder_path, filename)
       
        total_cfp, breakdown = self.calculate_footprint(items)
        
        if not breakdown:
            print("No valid food items to plot.")
            return
        
        labels = breakdown.keys()
        values = [item_data['total_cfp'] for item_data in breakdown.values()]
       
        percentages = [(v / total_cfp) * 100 for v in values]
       
        labels_with_pct = [f"{label} ({pct:.1f}%)" for label, pct in zip(labels, percentages)]
        
        plt.figure(figsize=(10, 8))

        colors = plt.cm.Spectral(np.linspace(0, 1, len(labels)))
        
        plt.pie(values, labels=labels_with_pct, autopct='%1.1f%%', startangle=90, 
                colors=colors, shadow=True, explode=[0.05] * len(labels),
                textprops={'fontsize': 12})
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(f'Carbon Footprint Breakdown: {meal_name}\nTotal: {total_cfp:.2f} kg CO₂', fontsize=16)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Meal breakdown plot saved to {save_path}")
        else:
            plt.show()
    
    def interactive_meal_input(self):
        """
        Interactive command-line interface for entering meal details.
        
        Returns:
            tuple: (meal_name, items)
                meal_name (str): The name of the meal
                items (list): List of (food_item, quantity) tuples
        """
        print("\n=== Carbon Footprint Meal Calculator ===\n")
        
        meal_name = input("Please enter the meal name (e.g., Breakfast/Lunch/Dinner): ")
       
        print("\nAvailable food items:")
        columns = 3
        food_items_chunks = [self.food_list[i:i + columns] for i in range(0, len(self.food_list), columns)]
        
        for chunk in food_items_chunks:
            print("  ".join(f"{item:<20}" for item in chunk))
        
        while True:
            try:
                item_count = int(input("\nHow many food items will you eat? "))
                if item_count > 0:
                    break
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
      
        items = []
        print("\nEnter food items one by one:")
        
        for i in range(item_count):
            while True:
                try:
                    print(f"\nItem {i+1}:")
                    item = input("Food item: ").lower().strip()
                    
                    if item not in self.food_list:
                        closest_matches = [food for food in self.food_list if item in food]
                        if closest_matches:
                            print(f"Item '{item}' not found. Did you mean one of these?")
                            for match in closest_matches[:5]:  # Show up to 5 suggestions
                                print(f"  - {match}")
                            continue
                        else:
                            print(f"Item '{item}' not found in the database.")
                            print("Please enter a food item from the list above.")
                            continue
                   
                    quantity = float(input("Quantity (kg): "))
                    if quantity <= 0:
                        print("Quantity must be greater than zero.")
                        continue
                   
                    items.append((item, quantity))
                    break
                except ValueError:
                    print("Please enter a valid quantity (e.g., 0.5).")
        
        return meal_name, items
    
    def display_results(self, meal_name, items):
        """
        Display the carbon footprint results for a meal.
        
        Args:
            meal_name (str): Name of the meal
            items (list): List of (food_item, quantity) tuples
        """
        total_cfp, breakdown = self.calculate_footprint(items)
        
        print("\n=== Results ===\n")
        print(f"Meal: {meal_name}")
        print(f"Total Carbon Footprint: {total_cfp:.2f} kg CO₂ equivalents\n")
        
        table_data = []
        for item, data in breakdown.items():
            table_data.append([
                item,
                f"{data['quantity']:.2f} kg",
                f"{data['unit_cfp']:.2f} kg CO₂/kg",
                f"{data['total_cfp']:.2f} kg CO₂",
                f"{(data['total_cfp'] / total_cfp * 100):.1f}%"
            ])
        
        print(tabulate(
            table_data,
            headers=["Food Item", "Quantity", "CO₂/kg", "Total CO₂", "% of Meal"],
            tablefmt="grid"
        ))
        
        high_impact_items = sorted(
            breakdown.items(),
            key=lambda x: x[1]['total_cfp'],
            reverse=True
        )
        
        if high_impact_items:
            highest_item = high_impact_items[0][0]
            alternatives = self.suggest_alternatives(highest_item)
            
            if alternatives:
                print(f"\nTo reduce your carbon footprint, consider these alternatives to {highest_item}:")
                for alt, cfp in alternatives:
                    reduction = (breakdown[highest_item]['unit_cfp'] - cfp) / breakdown[highest_item]['unit_cfp'] * 100
                    print(f"  - {alt}: {cfp:.2f} kg CO₂/kg ({reduction:.1f}% less impact)")
    
    def save_results(self, meal_name, items, filename='Meal_Carbon_Footprint.xlsx'):
        """
        Save the carbon footprint calculation results to an Excel file.
        
        Args:
            meal_name (str): Name of the meal
            items (list): List of (food_item, quantity) tuples
            filename (str): Name of the output Excel file
        """
        total_cfp, breakdown = self.calculate_footprint(items)
        
        details_data = []
        for item, data in breakdown.items():
            details_data.append({
                'Food Item': item,
                'Quantity (kg)': data['quantity'],
                'CO₂/kg': data['unit_cfp'],
                'Total CO₂': data['total_cfp'],
                'Percentage': data['total_cfp'] / total_cfp * 100
            })
        
        details_df = pd.DataFrame(details_data)
       
        summary_data = {
            'Meal Name': [meal_name],
            'Item Count': [len(items)],
            'Items': [str(items)],
            'Total Carbon Footprint (kg CO₂)': [total_cfp]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        with pd.ExcelWriter(filename) as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            details_df.to_excel(writer, sheet_name='Details', index=False)
        
        print(f"\nResults saved to {filename}")

def main():
    """Main function to run the carbon footprint calculator"""
    parser = argparse.ArgumentParser(description='Calculate the carbon footprint of the meals')
    parser.add_argument('--data', type=str, default='Food_Production.csv',
                        help='Path to the food production data CSV file')
    parser.add_argument('--visualize-only', action='store_true',
                        help='Only generate the food comparison visualization')
    args = parser.parse_args()
    
    calculator = CarbonFootprintCalculator(args.data)
    
    if args.visualize_only:
        calculator.plot_food_comparison(None)
        sys.exit(0)
   
    meal_name, items = calculator.interactive_meal_input()
   
    calculator.display_results(meal_name, items)
    calculator.plot_meal_breakdown(meal_name, items, f"{meal_name.lower().replace(' ', '_')}_breakdown.png")
    
    calculator.save_results(meal_name, items)
    print("\nThank you for using the Carbon Footprint Calculator!")

if __name__ == "__main__":
    main()