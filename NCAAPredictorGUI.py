import tkinter as tk
from tkinter import ttk, messagebox

# Coefficients from Dummy_Model_Clean (506 players, outliers removed)
coefficients = {
    'Intercept': 83.40709,
    'HC_Moti.1': 0.35494,
    'HC_Moti.2': 2.03755,
    'OC_Moti.1': 0.62476,
    'DC_Moti.1': 3.16875,
    'HC_TD1': 9.49064,
    'HC_TD2': 2.77841,
    'HC_TD3': -0.33346,
    'OC_TD1': 3.08600,
    'OC_TD2': 1.82702,
    'OC_TD3': 2.45405,
    'DC_TD1': -1.44690,
    'DC_TD2': 14.21596,
    'DC_TD3': 13.07231,
    'XP_Penalty': -0.42761
}

# Development Trait coefficients (baseline is Elite)
dev_trait_coeffs = {
    'Elite': 0,  # baseline
    'Impact': -38.18651,
    'Normal': -50.53085,
    'Star': -23.53652
}

# Position coefficients (baseline is QB - not in model)
position_coeffs = {
    'QB': 0,  # baseline
    'RB': -4.687237,
    'WR': -0.3681322,
    'TE': -6.699325,
    'OL': 3.123435,
    'DL': -6.514467,
    'DT': -3.839926,
    'LB': -10.68404,
    'S': -2.186808,
    'CB': 0.5434067,
    'K': 0.2088728,
    'P': 0.8526459
}

# Year coefficients (baseline is FR - not in model)
year_coeffs = {
    'FR': 0,  # baseline
    'FR (RS)': -2.86779,
    'SO': -3.145401,
    'SO (RS)': -5.05219,
    'JR': -4.748136,
    'JR (RS)': -2.66559,
    'SR': 0.08653364
}

# Binary mapping
binary_map = {"Yes": 1, "No": 0}

# Variable labels
variable_labels = {
    'HC_Moti.1': 'HC Motivator Tier 1',
    'HC_Moti.2': 'HC Motivator Tier 2',
    'OC_Moti.1': 'OC Motivator Tier 1',
    'DC_Moti.1': 'DC Motivator Tier 1',
    'HC_TD1': 'HC Talent Developer Tier 1',
    'HC_TD2': 'HC Talent Developer Tier 2',
    'HC_TD3': 'HC Talent Developer Tier 3',
    'OC_TD1': 'OC Talent Developer Tier 1',
    'OC_TD2': 'OC Talent Developer Tier 2',
    'OC_TD3': 'OC Talent Developer Tier 3',
    'DC_TD1': 'DC Talent Developer Tier 1',
    'DC_TD2': 'DC Talent Developer Tier 2',
    'DC_TD3': 'DC Talent Developer Tier 3'
}

# Model performance statistics
MODEL_STATS = {
    'r_squared': 0.9322,
    'adj_r_squared': 0.9273,
    'mae': 4.38,
    'rmse': 5.65,
    'n': 506,
    # Overall accuracy ranges
    'accuracy_ranges': [
        {'range': 5, 'percentage': 58.7},
        {'range': 7.5, 'percentage': 76.48},
        {'range': 10, 'percentage': 89.33},
        {'range': 20, 'percentage': 100.0},
        {'range': 25, 'percentage': 100.0}
    ]
}

# DevT-specific accuracy data
DEVT_ACCURACY = {
    'Elite': {
        'n': 11,
        'mae': 8.62,
        'ranges': [
            {'range': 5, 'percentage': 27.3},
            {'range': 10, 'percentage': 63.6},
            {'range': 15, 'percentage': 90.9}
        ]
    },
    'Impact': {
        'n': 250,
        'mae': 4.05,
        'ranges': [
            {'range': 5, 'percentage': 68.8},
            {'range': 10, 'percentage': 94.8},
            {'range': 15, 'percentage': 99.2}
        ]
    },
    'Normal': {
        'n': 116,
        'mae': 5.5,
        'ranges': [
            {'range': 5, 'percentage': 51.7},
            {'range': 10, 'percentage': 82.8},
            {'range': 15, 'percentage': 99.1}
        ]
    },
    'Star': {
        'n': 129,
        'mae': 5.39,
        'ranges': [
            {'range': 5, 'percentage': 48.1},
            {'range': 10, 'percentage': 86.8},
            {'range': 15, 'percentage': 97.7}
        ]
    }
}

class SkillPointsPredictor:
    def __init__(self, root):
        self.root = root
        self.root.title("NCAA 26 Skill Points Predictor")
        self.root.geometry("600x700")  # Shorter window to force scrolling
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(root, width=580, height=680)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container with padding
        main_frame = scrollable_frame
        
        # Title
        title = tk.Label(main_frame, text="NCAA 26 Skill Points Predictor", 
                        font=('Arial', 14, 'bold'), fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # Subtitle with version
        subtitle = tk.Label(main_frame, text=f"v2.1 | Clean Model (R² = {MODEL_STATS['r_squared']:.4f}, MAE = {MODEL_STATS['mae']:.2f})", 
                           font=('Arial', 8), fg='#7f8c8d')
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 8))
        
        self.entries = {}
        row_num = 2
        
        # Player Info Section
        section_label = tk.Label(main_frame, text="Player Information", 
                                font=('Arial', 10, 'bold'), fg='#34495e')
        section_label.grid(row=row_num, column=0, columnspan=2, sticky='w', pady=(3, 2))
        row_num += 1
        
        # Position dropdown
        tk.Label(main_frame, text="Position:", font=('Arial', 9)).grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        self.position_var = tk.StringVar()
        self.position_var.set("QB")
        position_dropdown = ttk.Combobox(main_frame, textvariable=self.position_var, 
                                        values=list(position_coeffs.keys()), 
                                        state='readonly', width=25)
        position_dropdown.grid(row=row_num, column=1, padx=5, pady=2, sticky='w')
        row_num += 1
        
        # Year dropdown
        tk.Label(main_frame, text="Year:", font=('Arial', 9)).grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        self.year_var = tk.StringVar()
        self.year_var.set("FR")
        year_dropdown = ttk.Combobox(main_frame, textvariable=self.year_var, 
                                    values=list(year_coeffs.keys()), 
                                    state='readonly', width=25)
        year_dropdown.grid(row=row_num, column=1, padx=5, pady=2, sticky='w')
        row_num += 1
        
        # Developer Trait dropdown
        tk.Label(main_frame, text="Development Trait:", font=('Arial', 9)).grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        self.dev_var = tk.StringVar()
        self.dev_var.set("Normal")
        dev_dropdown = ttk.Combobox(main_frame, textvariable=self.dev_var, 
                                    values=list(dev_trait_coeffs.keys()), 
                                    state='readonly', width=25)
        dev_dropdown.grid(row=row_num, column=1, padx=5, pady=2, sticky='w')
        row_num += 1
        
        # XP Penalty Section
        section_label = tk.Label(main_frame, text="Penalty Slider", 
                                font=('Arial', 10, 'bold'), fg='#34495e')
        section_label.grid(row=row_num, column=0, columnspan=2, sticky='w', pady=(6, 2))
        row_num += 1
        
        tk.Label(main_frame, text="XP Penalty Slider:", font=('Arial', 9)).grid(
            row=row_num, column=0, padx=5, pady=2, sticky='w')
        self.xp_entry = ttk.Entry(main_frame, width=27)
        self.xp_entry.insert(0, "0")
        self.xp_entry.grid(row=row_num, column=1, padx=5, pady=2, sticky='w')
        row_num += 1
        
        # Coaching Traits Section
        section_label = tk.Label(main_frame, text="Coach Abilities", 
                                font=('Arial', 10, 'bold'), fg='#34495e')
        section_label.grid(row=row_num, column=0, columnspan=2, sticky='w', pady=(6, 2))
        row_num += 1
        
        # Create yes/no dropdowns for coaching abilities
        for var, label in variable_labels.items():
            tk.Label(main_frame, text=f"{label}:", font=('Arial', 9)).grid(
                row=row_num, column=0, padx=5, pady=2, sticky='w')
            var_option = tk.StringVar()
            var_option.set("No")
            dropdown = ttk.Combobox(main_frame, textvariable=var_option, 
                                   values=list(binary_map.keys()), 
                                   state='readonly', width=25)
            dropdown.grid(row=row_num, column=1, padx=5, pady=2, sticky='w')
            self.entries[var] = var_option
            row_num += 1
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=8)
        
        # Predict button
        predict_btn = tk.Button(button_frame, text="Predict Skill Points", 
                               command=self.predict_skill,
                               bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                               padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        predict_btn.grid(row=0, column=0, padx=5)
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="Reset", 
                             command=self.reset_fields,
                             bg='#95a5a6', fg='white', font=('Arial', 11, 'bold'),
                             padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        reset_btn.grid(row=0, column=1, padx=5)
        
        # Result display
        self.result_frame = ttk.Frame(main_frame, relief=tk.SOLID, borderwidth=2)
        self.result_frame.grid(row=row_num+1, column=0, columnspan=2, pady=6, sticky='ew')
        
        self.result_label = tk.Label(self.result_frame, text="", 
                                     font=('Arial', 13, 'bold'), fg='#27ae60', pady=6)
        self.result_label.pack()
        
        # Confidence range display
        self.ci_frame = ttk.Frame(main_frame, relief=tk.GROOVE, borderwidth=1, padding=6)
        self.ci_frame.grid(row=row_num+2, column=0, columnspan=2, pady=4, sticky='ew')
        
        ci_title = tk.Label(self.ci_frame, text="Prediction Accuracy:", 
                           font=('Arial', 10, 'bold'), fg='#2c3e50')
        ci_title.pack(anchor='w', pady=(0, 5))
        
        self.ci_label = tk.Label(self.ci_frame, text="", 
                                font=('Arial', 9), fg='#34495e', justify=tk.LEFT)
        self.ci_label.pack(anchor='w')
        
        # Info label
        info_text = f"59% of predictions within ±5 points | 89% within ±10 points"
        info_label = tk.Label(main_frame, text=info_text, 
                             font=('Arial', 8), fg='#7f8c8d')
        info_label.grid(row=row_num+3, column=0, columnspan=2, pady=(8, 0))
    
    def predict_skill(self):
        try:
            # Start with intercept
            prediction = coefficients['Intercept']
            
            # Add position effect
            position = self.position_var.get()
            prediction += position_coeffs[position]
            
            # Add year effect
            year = self.year_var.get()
            prediction += year_coeffs[year]
            
            # Add developer trait effect
            dev_trait = self.dev_var.get()
            prediction += dev_trait_coeffs[dev_trait]
            
            # Get XP penalty and add its effect
            xp_penalty = float(self.xp_entry.get())
            prediction += coefficients['XP_Penalty'] * xp_penalty
            
            # Add coaching traits
            for var, var_option in self.entries.items():
                val = binary_map[var_option.get()]
                prediction += coefficients[var] * val
            
            # Display main prediction
            result_text = f"Predicted: {prediction:.1f} skill points"
            self.result_label.config(text=result_text, fg='#27ae60')
            
            # Get DevT-specific accuracy data
            devt_stats = DEVT_ACCURACY[dev_trait]
            
            # Display DevT-specific accuracy ranges
            ci_text = f"Accuracy for {dev_trait} players (based on {devt_stats['n']} players):\n"
            ci_text += f"Typical error: ±{devt_stats['mae']:.1f} points\n\n"
            
            for acc in devt_stats['ranges']:
                range_val = acc['range']
                pct = acc['percentage']
                lower = max(0, prediction - range_val)
                upper = prediction + range_val
                
                ci_text += f"±{int(range_val)} points ({pct:.1f}% of the time): {lower:.1f} - {upper:.1f}\n"
            
            self.ci_label.config(text=ci_text.strip())
            
            # Show detailed breakdown in console
            self.show_breakdown(prediction, position, year, dev_trait, xp_penalty)
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for XP Penalty")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def show_breakdown(self, total, position, year, dev_trait, xp_penalty):
        """Show detailed breakdown of prediction"""
        breakdown = f"\n--- Prediction Breakdown ---\n"
        breakdown += f"Base: {coefficients['Intercept']:.2f}\n"
        breakdown += f"Position ({position}): {position_coeffs[position]:+.2f}\n"
        breakdown += f"Year ({year}): {year_coeffs[year]:+.2f}\n"
        breakdown += f"Dev Trait ({dev_trait}): {dev_trait_coeffs[dev_trait]:+.2f}\n"
        breakdown += f"XP Penalty: {coefficients['XP_Penalty'] * xp_penalty:+.2f}\n"
        
        traits_sum = sum(coefficients[var] * binary_map[var_option.get()] 
                        for var, var_option in self.entries.items())
        breakdown += f"Coaching Traits: {traits_sum:+.2f}\n"
        breakdown += f"\nTotal: {total:.2f} points"
        
        print(breakdown)
    
    def reset_fields(self):
        """Reset all fields to default values"""
        self.position_var.set("QB")
        self.year_var.set("FR")
        self.dev_var.set("Normal")
        self.xp_entry.delete(0, tk.END)
        self.xp_entry.insert(0, "0")
        for var_option in self.entries.values():
            var_option.set("No")
        self.result_label.config(text="")
        self.ci_label.config(text="")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SkillPointsPredictor(root)
    root.mainloop()