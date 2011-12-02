# vim: et:sta:bs=2:sw=4:

import threading

from mirte.core import Module
from sarah.event import Event

class State(Module):
    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
        self.on_occupation_changed = Event()
        self.on_roomMap_changed = Event()
        self.occupation = {}
        self.roomMap = {}
        self.occupationVersion = 0
        self.roomMapVersion = 0
        self.lock = threading.Lock()
    def push_occupation_changes(self, occ, source='unknown'):
        roomMap_changed = False
        processed_occ = {}
        with self.lock:
            for pc, state in occ.iteritems():
                pc = pc.lower() # normalize HG075PC47 -> hg075pc47
                # TODO do not hardcode this
                if pc.startswith('cz'):
                    continue
                if pc not in self.occupation or self.occupation[pc] != state:
                    processed_occ[pc] = state
                    self.occupation[pc] = state
                # TODO pull roomMap from ethergids instead of using these
                # heuristics
                roomBit, pcBit = pc.split('pc')
                room = {'hg761': 'HG03.761',
                    'hg206': 'HG02.206',
                    'hg201': 'HG00.201',
                    'hg153': 'HG00.153',
                    'hg137': 'HG00.137',
                    'hg075': 'HG00.075',
                    'hg029': 'HG00.029',
                    'hg023': 'HG00.023',
                    'bib': 'Library of Science',
                    'info': 'Infozuilen'}.get(roomBit, roomBit)
                if not room in self.roomMap:
                    self.roomMap[room] = []
                    roomMap_changed = True
                if not pc in self.roomMap[room]:
                    self.roomMap[room].append(pc)
                    roomMap_changed = True
            if roomMap_changed:
                roomMap = dict(self.roomMap)
        if roomMap_changed:
            self.roomMapVersion += 1
            self.on_roomMap_changed(roomMap, self.roomMapVersion)
        if processed_occ:
            self.occupationVersion += 1
            self.on_occupation_changed(processed_occ, source,
                            self.occupationVersion)
    def get_occupation(self):
        with self.lock:
            return (dict(self.occupation), self.occupationVersion)
    def get_roomMap(self):
        with self.lock:
            return (dict(self.roomMap), self.roomMapVersion)