from rectangle import Rectangle

note_step = 0.0625

note_defs = {
     -4 : ("g5", 79,"솔5"),
     -3 : ("f5", 77,"파5"),
     -2 : ("e5", 76,"미5"),
     -1 : ("d5", 74,"레5"),
      0 : ("c5", 72,"도5"), #도 
      1 : ("b4", 71,"시4"), 
      2 : ("a4", 69,"라4"),
      3 : ("g4", 67,"솔4"),
      4 : ("f4", 65,"파4"),
      5 : ("e4", 64,"미4"), 
      6 : ("d4", 62,"레4"), 
      7 : ("c4", 60,"도4"),
      8 : ("b3", 59,"시3"), #시 
      9 : ("a3", 57,"라3"), 
     10 : ("g3", 55,"솔3"),
     11 : ("f3", 53,"파3"),
     12 : ("e3", 52,"미3"),
     13 : ("d3", 50,"레3"),
     14 : ("c3", 48,"도3"),
     15 : ("b2", 47,"시2"),
     16 : ("a2", 45,"라2"),
     17 : ("f2", 53,"파2"),
}

class Note(object):
    def __init__(self, rec, sym, staff_rec, sharp_notes = [], flat_notes = []):
        """
        rec = 객체
        sym = 명시된 객체의 이름
        staff_rec = 오선 하나를 둘러싼 객체
        """
        self.rec = rec
        self.sym = sym

        #중간값 객체의 y좌표(맨 아래) + 객체의 높이/2 (반) = 중간y좌표
        middle = rec.y + (rec.h / 2.0)
        #높이 = 중간y좌표 - 오선의 맨 아래 y좌표 / 오선의 높이
        height = (middle - staff_rec.y) / staff_rec.h
        print(height,staff_rec.y,staff_rec.h)

        #해당 객체의 높이에 따른 인덱싱
        note_def = note_defs[int(height/note_step + 0.5)]
        self.note = note_def[0]
        print(sym)
        self.pitch = note_def[1]
        self.note_kor = note_def[2]
        if any(n for n in sharp_notes if n.note[0] == self.note[0]):
            self.note += "#"
            self.pitch += 1
        if any(n for n in flat_notes if n.note[0] == self.note[0]):
            self.note += "b"
            self.pitch -= 1
        

