import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')

class BatteryCharging:
    def __init__(self, BatteryCapacity_kWh):
        self.BatteryCapacity_kWh = BatteryCapacity_kWh
        self.BatteryCapacity_J = BatteryCapacity_kWh * 3600 * 1000

    def chargeBattery_continuous(self, Pelec, t, visualise=True):
        cumulative_energy_J = sp.integrate.cumulative_trapezoid(y=Pelec, x=t, initial=0)
        num_batteries_charged = int(cumulative_energy_J[-1] / self.BatteryCapacity_J)

        charge_times_hr = []
        for ibattery in range(1, num_batteries_charged + 1):
            energy_needed = ibattery * self.BatteryCapacity_J
            charge_time_index = np.where(cumulative_energy_J >= energy_needed)[0][0]
            charge_times_hr.append(t[charge_time_index] / 3600)

        wrapped_cumulative_energy_J = cumulative_energy_J % self.BatteryCapacity_J
        charge_times_hr_diff = np.diff(np.insert(charge_times_hr, 0, 0))

        if visualise:
            plt.subplot(2, 1, 1)
            plt.plot(t / (3600 * 24), wrapped_cumulative_energy_J)
            plt.title(f'Battery Capacity: {self.BatteryCapacity_kWh} kWh')
            plt.xlabel('Time [days]')
            plt.ylabel('Battery Charged')
            plt.grid(True, axis='y')
            plt.tight_layout()

            plt.subplot(2, 1, 2)
            plt.bar(range(num_batteries_charged), charge_times_hr_diff / 24, tick_label=[f'B{i + 1}' for i in range(num_batteries_charged)])
            plt.xlabel('Battery Number')
            plt.ylabel('Time to full charge each battery [days]')
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.show()

        return num_batteries_charged, charge_times_hr

    def chargeBattery_perDay(self, Pelec, t, visualise=True):
        dt = t[2] - t[1]
        lenPerDay = int((24 * 3600) / dt)
        reshaped_time = np.reshape(t, (-1, lenPerDay))
        reshaped_Pelec = np.reshape(Pelec, (-1, lenPerDay))

        battery_capacity_Wh = self.BatteryCapacity_kWh * 1000  # 1 kWh = 1000 Wh

        percent_charged_list = []
        time_to_full_charged_list_hr = []
        cumulative_energy_list_kWh = []

        for irow in range(len(reshaped_Pelec)):
            cumulative_energy_J = sp.integrate.cumulative_trapezoid(y=reshaped_Pelec[irow, :], x=reshaped_time[irow, :], initial=0)
            cumulative_energy_Wh = cumulative_energy_J / 3600

            if visualise:
                plt.subplot(2, 1, 1)
                plt.plot(reshaped_time[irow, :], reshaped_Pelec[irow, :])
                plt.title('Electrical Power Profile [W]')
                plt.xlabel('Time (s)')
                plt.ylabel('Power (W)')

                plt.subplot(2, 1, 2)
                plt.plot(reshaped_time[irow, :], cumulative_energy_Wh / 1000)
                plt.title('Cumulative Energy Per Day [kWh]')
                plt.xlabel('Time (s)')
                plt.ylabel('Energy (kWh)')

            percent_charged = (cumulative_energy_Wh[-1] / battery_capacity_Wh) * 100
            percent_charged = min(percent_charged, 100)
            percent_charged_list.append(percent_charged)
            cumulative_energy_list_kWh.append(cumulative_energy_Wh[-1] / 1000)

            try:
                charging_time_index = np.searchsorted(cumulative_energy_Wh, battery_capacity_Wh)
                charging_time_seconds = reshaped_time[irow, charging_time_index] - reshaped_time[irow, 0]
                charging_time_hours = charging_time_seconds / 3600
                time_to_full_charged_list_hr.append(charging_time_hours)
            except IndexError:
                charging_time_hours = 0.0
                time_to_full_charged_list_hr.append(charging_time_hours)

        if visualise:
            plt.tight_layout()
            plt.show()

        if visualise:
            plt.subplot(2, 1, 1)
            plt.bar(range(len(percent_charged_list)), percent_charged_list, tick_label=[f'D{i + 1}' for i in range(len(percent_charged_list))])
            plt.title(f'Battery Capacity: {self.BatteryCapacity_kWh} kWh')
            plt.xlabel('Days')
            plt.ylabel('Percentage Charged (%)')
            plt.ylim(0, 100)
            plt.grid(True, axis='y')
            plt.tight_layout()

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

