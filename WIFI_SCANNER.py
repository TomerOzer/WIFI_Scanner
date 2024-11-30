import pywifi
import time
import tkinter as tk
from tkinter import simpledialog
from colorama import Fore, Style, init
class WIFI_SCANNER:
    def __init__(self, windX=450, windY=400):
        self.bg = "#010417"
        self.windX = windX
        self.windY = windY
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        init(autoreset=True)

        self.window = tk.Tk()
        self.window.title("Wi-Fi Interface")
        self.window.geometry(f"{windX}x{windY}")
        self.window.configure(bg=self.bg)
        self.window.resizable(width=False, height=False)

        title = tk.Label(self.window, text="Wi-Fi Interface", font=("Arial", 20), bg=self.bg, fg="white" )
        title.pack(pady=10)

        self.current_network_label = tk.Label(self.window, text="Connected to: Checking...", font=("Arial", 12),
            bg=self.bg, fg="white",)
        self.current_network_label.pack(pady=10)

        self.networks_frame = tk.Frame(self.window, bg=self.bg)
        self.networks_frame.pack(pady=10, fill="both", expand=True)

        scan_button = tk.Button(self.window, text="Scan for Networks", command=self.scan_and_display_networks,
            bg="white", fg="black", font=("Arial", 10),)
        scan_button.pack(pady=10)

        if not self.iface:
            raise Exception(
                f"{Fore.RED}{Style.BRIGHT}Wi-Fi isn't available! Try turning on Wi-Fi!{Style.RESET_ALL}"
            )
        else:
            print(f"{Fore.GREEN}{Style.BRIGHT}Wi-Fi interface is available{Style.RESET_ALL}")

        self.update_connection_status()

        self.window.mainloop()

    def is_connected(self):
        profile = self.iface.status()
        if profile == pywifi.const.IFACE_CONNECTED:
            return self.iface.network_profiles()[0].ssid
        return None

    def update_connection_status(self):
        current_network = self.is_connected()
        self.current_network_label.config(
            text=f"Connected to: {current_network if current_network else 'No Network'}"
        )
        self.window.after(5000, self.update_connection_status)

    def scan_networks(self, dur=2.5):
        self.iface.scan()
        print(f"{Fore.CYAN}Searching for networks... {dur}s{Style.RESET_ALL}")
        time.sleep(dur)

        networks = self.iface.scan_results()
        filtered_networks = {}

        for i in networks:
            ssid = i.ssid
            signal = i.signal
            if ssid not in filtered_networks or signal > filtered_networks[ssid]:
                filtered_networks[ssid] = signal

        print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Available Networks:{Style.RESET_ALL}")
        for index, (netName, signal) in enumerate(filtered_networks.items(), 1):
            print(f"{index}. {netName} Signal Value: {signal}")
        print("\n")

        return filtered_networks

    def scan_and_display_networks(self):
        for widget in self.networks_frame.winfo_children():
            widget.destroy()

        networks = self.scan_networks()
        for ssid, signal in networks.items():
            network_button = tk.Button( self.networks_frame, text=f"{ssid} (Signal: {signal})",
                command=lambda ssid=ssid: self.prompt_password_and_connect(ssid), bg="white",
                fg="black", font=("Arial", 10), anchor="w", justify="left",
            )
            network_button.pack(fill="x", padx=5, pady=2)

    def prompt_password_and_connect(self, ssid):
        password = simpledialog.askstring(
            "Enter Password", f"Enter password for {ssid}:", show="*"
        )
        if password:
            self.connect_network(ssid, password)

    def connect_network(self, net, password):
        profile = pywifi.Profile()
        profile.ssid = net
        profile.key = password

        profile.auth = pywifi.const.AUTH_ALG_OPEN
        profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
        profile.cipher = pywifi.const.CIPHER_TYPE_CCMP

        self.iface.remove_all_network_profiles()
        temp_profile = self.iface.add_network_profile(profile)

        self.iface.connect(temp_profile)
        print(f"{Fore.LIGHTCYAN_EX}Connecting to {net}...{Style.RESET_ALL}")
        time.sleep(3)

        if self.iface.status() == pywifi.const.IFACE_CONNECTED:
            print(f"{Fore.GREEN}{Style.BRIGHT}Successfully connected to {net}!{Style.RESET_ALL}")
            tk.messagebox.showinfo("Connection Success", f"Connected to {net} successfully!")

            # Save the password to the file
            try:
                with open("Saved_Passwords.txt", "a") as file:
                    file.write(f"{net}: {password}\n")
            except Exception as e:
                print(f"{Fore.RED}Error saving password: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}Failed to connect to {net}. Please check the password.{Style.RESET_ALL}")
            tk.messagebox.showerror("Connection Failed", f"Failed to connect to {net}.")
