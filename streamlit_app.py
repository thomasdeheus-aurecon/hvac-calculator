import streamlit as st
import psychrolib
from typing import Optional

# Set psychrolib unit system (SI units)
psychrolib.SetUnitSystem(psychrolib.SI)

st.set_page_config(page_title="HVAC Calculator", page_icon="🌡️", layout="wide")

st.title("🌡️ HVAC Calculator")
st.write("A collection of useful HVAC calculations with psychrometric properties")

# Sidebar for calculation selection
st.sidebar.header("Select Calculation")
calculation_type = st.sidebar.selectbox(
    "Choose a calculation:",
    ["Heat Transfer (Q = m·c·ΔT)", "Psychrometric Properties"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("This app provides various HVAC calculations using the psychrolib library for psychrometric properties.")

# Fluid properties database
FLUID_PROPERTIES = {
    "Air": {
        "density": 1.225,  # kg/m³ at 15°C, sea level
        "specific_heat": 1005,  # J/kg·K
    },
    "Water": {
        "density": 998.2,  # kg/m³ at 20°C
        "specific_heat": 4182,  # J/kg·K
    }
}

# Main content area
if calculation_type == "Heat Transfer (Q = m·c·ΔT)":
    st.header("Heat Transfer Calculation")
    st.markdown("**Formula:** Q = m × c × ΔT")
    st.markdown("Where:")
    st.markdown("- Q = Heat transfer rate (W or kW)")
    st.markdown("- m = Mass flow rate (kg/s)")
    st.markdown("- c = Specific heat capacity (J/kg·K)")
    st.markdown("- ΔT = Temperature difference (K or °C)")
    
    st.markdown("---")
    
    # Fluid selection
    fluid_type = st.selectbox("Select Fluid Type:", ["Air", "Water"])
    
    # Get fluid properties
    density_default = FLUID_PROPERTIES[fluid_type]["density"]
    c_default = FLUID_PROPERTIES[fluid_type]["specific_heat"]
    
    # Display fluid properties
    prop_col1, prop_col2 = st.columns(2)
    with prop_col1:
        st.info(f"**{fluid_type} Density (ρ):** {density_default} kg/m³")
    with prop_col2:
        st.info(f"**{fluid_type} Specific Heat (c):** {c_default} J/kg·K")
    
    st.markdown("---")
    st.subheader("Input Values")
    st.info("Leave ONE field empty to solve for that variable")
    
    col1, col2 = st.columns(2)
    
    with col1:
        q_input = st.text_input("Heat Transfer Rate Q (kW)", "")
        v_input = st.text_input("Volume Flow Rate V (L/s)", "")
    
    with col2:
        delta_t_input = st.text_input("Temperature Difference ΔT (K or °C)", "")
    
    
    if st.button("Calculate", type="primary"):
        # Convert inputs to floats or None
        try:
            q = float(q_input) * 1000 if q_input.strip() else None  # Convert kW to W
            v = float(v_input) if v_input.strip() else None  # L/s
            delta_t = float(delta_t_input) if delta_t_input.strip() else None
            
            # Get fluid properties (always provided)
            density = density_default
            c = c_default
            
            # Count how many values are provided
            provided_values = sum([q is not None, v is not None, delta_t is not None])
            
            if provided_values != 2:
                st.error("❌ Please provide exactly 2 values and leave 1 blank to solve for it.")
            else:
                # Calculate mass flow rate from volume flow rate: m = V × ρ / 1000 (L/s to m³/s conversion)
                # Q = m × c × ΔT = (V × ρ / 1000) × c × ΔT
                
                st.success("✅ Calculation Results:")
                
                # Solve for the missing variable
                if q is None:
                    # Q = (V × ρ / 1000) × c × ΔT
                    m = v * density / 1000  # Convert L/s to kg/s
                    q = m * c * delta_t
                    st.metric("Heat Transfer Rate (Q)", f"{q/1000:.2f} kW", f"{q:.2f} W")
                elif v is None:
                    # V = (Q / (c × ΔT)) / ρ × 1000
                    m = q / (c * delta_t)
                    v = m * 1000 / density  # Convert kg/s to L/s
                    st.metric("Volume Flow Rate (V)", f"{v:.2f} L/s")
                elif delta_t is None:
                    # ΔT = Q / ((V × ρ / 1000) × c)
                    m = v * density / 1000
                    delta_t = q / (m * c)
                    st.metric("Temperature Difference (ΔT)", f"{delta_t:.2f} K (or °C)")
                
                # Calculate all derived values for display
                if v is not None and density is not None:
                    m = v * density / 1000
                    
                # Display all values
                st.markdown("---")
                st.subheader("Complete Set of Values:")
                results_col1, results_col2 = st.columns(2)
                with results_col1:
                    st.write(f"**Q:** {q/1000:.2f} kW ({q:.2f} W)")
                    st.write(f"**V:** {v:.2f} L/s")
                    st.write(f"**m:** {m:.4f} kg/s")
                with results_col2:
                    st.write(f"**ρ:** {density} kg/m³")
                    st.write(f"**c:** {c:.0f} J/kg·K")
                    st.write(f"**ΔT:** {delta_t:.2f} K (or °C)")
                
        except ValueError:
            st.error("❌ Please enter valid numerical values.")
        except ZeroDivisionError:
            st.error("❌ Cannot divide by zero. Please check your input values.")

elif calculation_type == "Psychrometric Properties":
    st.header("Psychrometric Properties")
    st.markdown("Calculate air properties using psychrolib")
    
    st.subheader("Input Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dry_bulb = st.number_input("Dry Bulb Temperature (°C)", value=25.0, step=0.1)
        pressure = st.number_input("Atmospheric Pressure (Pa)", value=101325, step=100)
    
    with col2:
        input_type = st.radio("Select input type:", ["Relative Humidity (%)", "Wet Bulb Temperature (°C)"])
        
        if input_type == "Relative Humidity (%)":
            rh = st.number_input("Relative Humidity (%)", value=50.0, min_value=0.0, max_value=100.0, step=1.0)
        else:
            wet_bulb = st.number_input("Wet Bulb Temperature (°C)", value=20.0, step=0.1)
    
    if st.button("Calculate Properties", type="primary"):
        try:
            # Calculate humidity ratio based on input type
            if input_type == "Relative Humidity (%)":
                hum_ratio = psychrolib.GetHumRatioFromRelHum(dry_bulb, rh/100, pressure)
            else:
                hum_ratio = psychrolib.GetHumRatioFromTWetBulb(dry_bulb, wet_bulb, pressure)
            
            # Calculate all properties
            rel_hum = psychrolib.GetRelHumFromHumRatio(dry_bulb, hum_ratio, pressure) * 100
            wet_bulb_calc = psychrolib.GetTWetBulbFromHumRatio(dry_bulb, hum_ratio, pressure)
            dew_point = psychrolib.GetTDewPointFromHumRatio(dry_bulb, hum_ratio, pressure)
            enthalpy = psychrolib.GetMoistAirEnthalpy(dry_bulb, hum_ratio)
            specific_volume = psychrolib.GetMoistAirVolume(dry_bulb, hum_ratio, pressure)
            
            st.success("✅ Calculated Properties:")
            
            # Display results in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Dry Bulb Temp", f"{dry_bulb:.2f} °C")
                st.metric("Wet Bulb Temp", f"{wet_bulb_calc:.2f} °C")
            
            with col2:
                st.metric("Dew Point", f"{dew_point:.2f} °C")
                st.metric("Relative Humidity", f"{rel_hum:.1f} %")
            
            with col3:
                st.metric("Humidity Ratio", f"{hum_ratio:.6f} kg/kg")
                st.metric("Enthalpy", f"{enthalpy/1000:.2f} kJ/kg")
            
            st.metric("Specific Volume", f"{specific_volume:.4f} m³/kg")
            
        except Exception as e:
            st.error(f"❌ Error calculating properties: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and PsychroLib*")
