"""
Meal Comparison Tool for Carbon Footprint Analysis

This script allows users to compare the carbon footprints of different meals
and visualize the differences, helping to make more environmentally conscious food choices.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import numpy as np
import argparse
from carbon_footprint_calculator import CarbonFootprintCalculator

class MealComparisonTool:
    """
    A tool for comparing the carbon footprints of different meals.
    """
    
    def __init__(self, data_file):
        """
        Initialize the meal comparison tool.
        
        Args:
            data_file (str): Path to the CSV file with food production carbon footprint data
        """
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Food_Production.csv")

        self.calculator = CarbonFootprintCalculator(data_file)
        self.meals = {}
    
    def add_meal(self, meal_name, items):
        """
        Add a meal to the comparison.
        
        Args:
            meal_name (str): Name of the meal
            items (list): List of (food_item, quantity) tuples
        """
        total_cfp, breakdown = self.calculator.calculate_footprint(items)
        
        self.meals[meal_name] = {
            'items': items,
            'total_cfp': total_cfp,
            'breakdown': breakdown
        }
        
        print(f"Added meal: {meal_name} with carbon footprint {total_cfp:.2f} kg CO₂")
    
    def interactive_add_meal(self):
        """Interactive method to add a meal through user input"""
        meal_name, items = self.calculator.interactive_meal_input()
        self.add_meal(meal_name, items)
    
    def compare_meals(self):
        """
        Display a comparison of all added meals.
        """
        if not self.meals:
            print("No meals to compare. Please add meals first.")
            return
        
        print("\n=== Meal Comparison ===\n")
        
        sorted_meals = sorted(self.meals.items(), key=lambda x: x[1]['total_cfp'])
        
        print(f"{'Meal':<20} {'Carbon Footprint (kg CO₂)':<25} {'Items'}")
        print("-" * 80)
        
        for meal_name, data in sorted_meals:
            items_str = ", ".join([f"{item[0]} ({item[1]}kg)" for item in data['items']])
            print(f"{meal_name:<20} {data['total_cfp']:<25.2f} {items_str}")
       
        lowest_cfp_meal = sorted_meals[0][0]
        highest_cfp_meal = sorted_meals[-1][0]
        
        print("\nThe meal with the lowest carbon footprint is:", lowest_cfp_meal)
        print("The meal with the highest carbon footprint is:", highest_cfp_meal)
        
        if len(sorted_meals) > 1:
            difference = self.meals[highest_cfp_meal]['total_cfp'] - self.meals[lowest_cfp_meal]['total_cfp']
            percentage = (difference / self.meals[highest_cfp_meal]['total_cfp']) * 100
            print(f"\nSwitching from {highest_cfp_meal} to {lowest_cfp_meal} would reduce your carbon footprint")
            print(f"by {difference:.2f} kg CO₂ ({percentage:.1f}% reduction).")
    
    def plot_meal_comparison(self, save_path=None):
        """
        Create a bar chart comparing the carbon footprints of different meals.
        
        Args:
            save_path (str, optional): Path to save the figure. 
        """
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

        if not self.meals:
            print("No meals to compare. Please add meals first.")
            return
       
        meal_names = list(self.meals.keys())
        carbon_footprints = [data['total_cfp'] for data in self.meals.values()]
        
        df = pd.DataFrame({
            'Meal': meal_names,
            'Carbon Footprint (kg CO₂)': carbon_footprints
        })
        
        df = df.sort_values('Carbon Footprint (kg CO₂)')
        
        plt.figure(figsize=(12, 8))
        
        sns.set_style("whitegrid")
        barplot = sns.barplot(x='Carbon Footprint (kg CO₂)', y='Meal', data=df, palette='viridis')
       
        for i, v in enumerate(df['Carbon Footprint (kg CO₂)']):
            barplot.text(v + 0.1, i, f"{v:.2f}", va='center')
        
        plt.title('Comparison of Meal Carbon Footprints', fontsize=16)
        plt.xlabel('Carbon Footprint (kg CO₂ equivalents)', fontsize=12)
        plt.ylabel('Meal', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Meal comparison plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_stacked_comparison(self, save_path=None):
        """
        Create a stacked bar chart showing the breakdown of carbon footprints by food item.
        """
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        
        if not self.meals or len(self.meals) < 2:
            print("Need at least two meals to create a stacked comparison.")
            return
       
        all_food_items = set()
        for meal_data in self.meals.values():
            all_food_items.update(meal_data['breakdown'].keys())
       
        data = []
        for meal_name, meal_data in self.meals.items():
            for food_item in all_food_items:
                if food_item in meal_data['breakdown']:
                    cfp = meal_data['breakdown'][food_item]['total_cfp']
                else:
                    cfp = 0
                
                data.append({
                    'Meal': meal_name,
                    'Food Item': food_item,
                    'Carbon Footprint': cfp
                })
        
        df = pd.DataFrame(data)
       
        pivot_df = df.pivot(index='Meal', columns='Food Item', values='Carbon Footprint')
        pivot_df = pivot_df.fillna(0)
        
        meal_order = [meal for meal, _ in sorted(
            self.meals.items(),
            key=lambda x: x[1]['total_cfp'],
            reverse=True
        )]
        pivot_df = pivot_df.reindex(meal_order)
      
        plt.figure(figsize=(14, 10))
        
        ax = pivot_df.plot(kind='barh', stacked=True, figsize=(14, 10), colormap='viridis')
        
        plt.title('Breakdown of Carbon Footprint by Food Item', fontsize=16)
        plt.xlabel('Carbon Footprint (kg CO₂ equivalents)', fontsize=12)
        plt.ylabel('Meal', fontsize=12)
       
        plt.legend(title='Food Item', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        for i, meal in enumerate(pivot_df.index):
            total = self.meals[meal]['total_cfp']
            ax.text(total + 0.2, i, f"{total:.2f}", va='center')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Stacked comparison plot saved to {save_path}")
        else:
            plt.show()
    
    def save_comparison(self, filename='Meal_Comparison.xlsx'):
        """
        Save the meal comparison data to an Excel file.
        """
        if not self.meals:
            print("No meals to save. Please add meals first.")
            return
       
        summary_data = []
        for meal_name, data in self.meals.items():
            summary_data.append({
                'Meal Name': meal_name,
                'Carbon Footprint (kg CO₂)': data['total_cfp'],
                'Item Count': len(data['items']),
                'Items': str(data['items'])
            })
        
        summary_df = pd.DataFrame(summary_data)
       
        details_data = []
        for meal_name, data in self.meals.items():
            for food_item, item_data in data['breakdown'].items():
                details_data.append({
                    'Meal': meal_name,
                    'Food Item': food_item,
                    'Quantity (kg)': item_data['quantity'],
                    'CO₂/kg': item_data['unit_cfp'],
                    'Total CO₂': item_data['total_cfp'],
                    'Percentage of Meal': item_data['total_cfp'] / data['total_cfp'] * 100
                })
        
        details_df = pd.DataFrame(details_data)
      
        with pd.ExcelWriter(filename) as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            details_df.to_excel(writer, sheet_name='Detailed Breakdown', index=False)
        
        print(f"\nComparison saved to {filename}")

def main():
    """Main function to run the meal comparison tool"""
    parser = argparse.ArgumentParser(description='Compare the carbon footprints of different meals')
    parser.add_argument('--data', type=str, default='Food_Production.csv',
                        help='Path to the food production data CSV file')
    args = parser.parse_args()
    
    comparison_tool = MealComparisonTool(args.data)
    
    while True:
        print("\n=== Meal Carbon Footprint Comparison Tool ===")
        print("1. Add a meal")
        print("2. Compare meals")
        print("3. Visualize meal comparison")
        print("4. Show detailed breakdown")
        print("5. Save comparison to Excel")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            comparison_tool.interactive_add_meal()
        elif choice == '2':
            comparison_tool.compare_meals()
            input("\nPress Enter to continue...")
        elif choice == '3':
            comparison_tool.plot_meal_comparison()
            if len(comparison_tool.meals) >= 2:
                print("\nAlso showing stacked breakdown comparison...")
                comparison_tool.plot_stacked_comparison()
        elif choice == '4':
            for meal_name, data in comparison_tool.meals.items():
                print(f"\n=== {meal_name} ===")
                comparison_tool.calculator.display_results(meal_name, data['items'])
                input("\nPress Enter to continue...")
        elif choice == '5':
            comparison_tool.save_comparison()
        elif choice == '6':
            print("\nThank you for using the Meal Carbon Footprint Comparison Tool!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()