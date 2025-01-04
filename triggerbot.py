import pymem
import pymem.process
import requests
import win32api, win32con
import time
import random

class TriggerBot:
    def __init__(self, random_delay=110, min_delay=240, key_bind="C", attack_all=False):
        self.random_delay = random_delay
        self.min_delay = min_delay
        self.key_bind = key_bind
        self.attack_all = attack_all
        self.pm, self.client = self.descriptor()
        self.offsets = self.get_offsets()

    def descriptor(self):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        return pm, client
    
    def get_offsets(self):
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()

        return {
            'dwEntityList': offsets['client.dll']['dwEntityList'],
            'dwLocalPlayerPawn': offsets['client.dll']['dwLocalPlayerPawn'],
            'm_iTeamNum': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum'],
            'm_iHealth': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth'],
            'm_iIDEntIndex': client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
        }
    
    def run(self):
        while True:
            if win32api.GetAsyncKeyState(ord(self.key_bind)):
                try:
                    player = self.pm.read_longlong(self.client + self.offsets['dwLocalPlayerPawn'])
                    entityId = self.pm.read_int(player + self.offsets['m_iIDEntIndex'])
                    if entityId > 0:
                        entList = self.pm.read_longlong(self.client + self.offsets['dwEntityList'])
                        entEntry = self.pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                        entity = self.pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                        entityTeam = self.pm.read_int(entity + self.offsets['m_iTeamNum'])
                        playerTeam = self.pm.read_int(player + self.offsets['m_iTeamNum'])
                        if self.attack_all or entityTeam != playerTeam:
                            entityHp = self.pm.read_int(entity + self.offsets['m_iHealth'])
                            if entityHp > 0:
                                sleep_in = random.randint(self.min_delay, (self.min_delay + self.random_delay))
                                time.sleep(sleep_in / 10000)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                                sleep_out = random.randint(self.min_delay, (self.min_delay + self.random_delay))
                                time.sleep(sleep_out / 10000)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                except:
                    time.sleep(0.03)
                    pass

if __name__ == "__main__":
    bot = TriggerBot()
    bot.run()