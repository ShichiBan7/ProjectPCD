class Riwayat:
    def __init__(self, batas=20):
        self.batas = batas
        self._undo = []
        self._redo = []

    def catat(self, state):
        """Dipanggil SEBELUM aksi dijalankan. Aksi baru menghapus jalur redo."""
        self._undo.append(state)
        if len(self._undo) > self.batas:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self, state_sekarang):
        if not self._undo:
            return None
        self._redo.append(state_sekarang)
        return self._undo.pop()

    def redo(self, state_sekarang):
        if not self._redo:
            return None
        self._undo.append(state_sekarang)
        return self._redo.pop()

    @property
    def bisa_undo(self):
        return bool(self._undo)

    @property
    def bisa_redo(self):
        return bool(self._redo)
