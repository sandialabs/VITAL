import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')

class BatteryCharging:
    def __init__(self, battery_capacity_kWh, number_of_turbines, turbulence_intensity):
        self.battery_capacity_kWh = battery_capacity_kWh
        self.battery_capacity_J = battery_capacity_kWh * 3600 * 1000
        self.number_of_turbines = number_of_turbines
        self.turbulence_intensity = turbulence_intensity
        self.instantaneous_power = None
        self.time_series = None

    def set_instantaneous_power(self, power_data, time_data):
        self.instantaneous_power = np.array(power_data) / (1 + self.turbulence_intensity) ** 3 * self.number_of_turbines
        self.time_series = np.array(time_data)

    def chargeBattery_continuous(self, power_electric, time_data, visualise=True):
        self.set_instantaneous_power(power_electric, time_data)

        cumulative_energy_J = integrate.cumulative_trapezoid(y=self.instantaneous_power, x=self.time_series, initial=0)
        num_batteries_charged = int(cumulative_energy_J[-1] / self.battery_capacity_J)

        charge_times_hr = []
        for ibattery in range(1, num_batteries_charged + 1):
            energy_needed = ibattery * self.battery_capacity_J
            charge_time_index = np.where(cumulative_energy_J >= energy_needed)[0][0]
            charge_times_hr.append(time_data[charge_time_index] / 3600)

        wrapped_cumulative_energy_J = cumulative_energy_J % self.battery_capacity_J
        charge_times_hr_diff = np.diff(np.insert(charge_times_hr, 0, 0))

        if visualise:
            plt.figure(figsize=(10, 8))
            plt.subplot(2, 1, 1)
            plt.plot(time_data / (3600 * 24), wrapped_cumulative_energy_J)
            plt.title(f'Battery Capacity: {self.battery_capacity_kWh} kWh')
            plt.xlabel('Time [days]')
            plt.ylabel('Battery Charged (J)')
            plt.grid(True, axis='y')

            plt.subplot(2, 1, 2)
            plt.bar(range(num_batteries_charged), charge_times_hr_diff / 24, tick_label=[f'B{i + 1}' for i in range(num_batteries_charged)])
            plt.xlabel('Battery Number')
            plt.ylabel('Time to full charge each battery [days]')
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.show()

        return num_batteries_charged, charge_times_hr_diff

    def chargeBattery_perDay(self, power_electric, time_data, visualise=True):
        self.set_instantaneous_power(power_electric, time_data)

        dt = self.time_series[1] - self.time_series[0]
        lenPerDay = int((24 * 3600) / dt)

        num_days = len(time_data) // lenPerDay
        time_series_truncated = self.time_series[:num_days * lenPerDay]
        instantaneous_power_truncated = self.instantaneous_power[:num_days * lenPerDay]

        reshaped_time = np.reshape(time_series_truncated, (-1, lenPerDay))
        reshaped_Pelec = np.reshape(instantaneous_power_truncated, (-1, lenPerDay))

        battery_capacity_Wh = self.battery_capacity_kWh * 1000  # 1 kWh = 1000 Wh

        percent_charged_list = []
        time_to_full_charged_list_hr = []
        cumulative_energy_list_kWh = []

        if visualise:
            plt.figure(figsize=(10, 8))

        for irow in range(len(reshaped_Pelec)):
            cumulative_energy_J = integrate.cumulative_trapezoid(y=reshaped_Pelec[irow, :], x=reshaped_time[irow, :], initial=0)
            cumulative_energy_Wh = cumulative_energy_J / 3600

            if visualise:
                plt.subplot(2, 1, 1)
                plt.plot(reshaped_time[irow, :], reshaped_Pelec[irow, :], label=f'Day {irow + 1}')
                plt.title('Electrical Power Profile [W]')
                plt.xlabel('Time (s)')
                plt.ylabel('Power (W)')

                plt.subplot(2, 1, 2)
                plt.plot(reshaped_time[irow, :], cumulative_energy_Wh / 1000, label=f'Day {irow + 1}')
                plt.title('Cumulative Energy Per Day [kWh]')
                plt.xlabel('Time (s)')
                plt.ylabel('Energy (kWh)')

            percent_charged = (cumulative_energy_Wh[-1] / battery_capacity_Wh) * 100
            percent_charged = min(percent_charged, 100)
            percent_charged_list.append(percent_charged)
            cumulative_energy_list_kWh.append(cumulative_energy_Wh[-1] / 1000)

            charging_time_index = np.searchsorted(cumulative_energy_Wh, battery_capacity_Wh)
            if charging_time_index < len(cumulative_energy_Wh):
                charging_time_seconds = reshaped_time[irow, charging_time_index] - reshaped_time[irow, 0]
                charging_time_hours = charging_time_seconds / 3600
                time_to_full_charged_list_hr.append(charging_time_hours)
            else:
                time_to_full_charged_list_hr.append(0.0)

        if visualise:
            plt.subplot(2, 1, 1)
            plt.legend()
            plt.tight_layout()

            plt.subplot(2, 1, 2)
            plt.legend()
            plt.tight_layout()
            plt.show()

            plt.figure(figsize=(10, 8))
            plt.subplot(2, 1, 1)
            plt.bar(range(len(percent_charged_list)), percent_charged_list, tick_label=[f'D{i + 1}' for i in range(len(percent_charged_list))])
            plt.title(f'Battery Capacity: {self.battery_capacity_kWh} kWh')
            plt.xlabel('Days')
            plt.ylabel('Percentage Charged (%)')
            plt.ylim(0, 100)
            plt.grid(True, axis='y')

            plt.subplot(2, 1, 2)
            plt.bar(range(len(percent_charged_list)), time_to_full_charged_list_hr, tick_label=[f'D{i + 1}' for i in range(len(percent_charged_list))])
            plt.xlabel('Days')
            plt.ylabel('Time to full charge [Hr]')
            plt.ylim(0, 24)
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.show()

        return {
            "days": range(len(percent_charged_list)),
            "time_to_full_charge_hr": time_to_full_charged_list_hr,
            "cumulative_energy_kWh": cumulative_energy_list_kWh,
            "percent_charged": percent_charged_list
        }
