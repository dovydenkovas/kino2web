from PySide6.QtWidgets import QVBoxLayout

from videoticket import VideoTicket


class TicketsView(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.tickets = []
        self.addStretch()

    def add_ticket(self, ticket: VideoTicket):
        self.tickets.append(ticket)
        ticket.delete_ticket.connect(self.delete_ticket)
        self.insertWidget(len(self.tickets) - 1, ticket)

    def delete_ticket(self, ticket: VideoTicket):
        for i in range(len(self.tickets)):
            if ticket is self.tickets[i]:
                self.removeWidget(ticket)
                ticket.deleteLater()
                self.tickets.pop(i)
                break

    def move_ticket(self, position, ticket):
        i = self.tickets.index(ticket)
        ticket = self.tickets.pop(i)
        self.tickets.insert(position, ticket)
        self.insertWidget(position, ticket)

    def __iter__(self) -> list[VideoTicket].__iter__:
        return self.tickets.__iter__()

    def __len__(self) -> int:
        return self.tickets.__len__()

    def __getitem__(self, item) -> VideoTicket:
        return self.tickets[item]
