from server_lib.session_record_manager import Record

class CSVBuilder:
    def build(data : list[Record]):
        txt = ""
        for record in data:
            txt += f"{record._velocity},{record._error_margin}\n"

        return txt