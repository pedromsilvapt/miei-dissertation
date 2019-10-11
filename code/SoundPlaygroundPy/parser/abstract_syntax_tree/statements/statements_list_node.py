from .statement_node import StatementNode

class StatementsListNode( StatementNode ):
    def __init__ ( self, nodes ):
        super().__init__()

        self.statements = nodes

    def get_events ( self, context ):
        for node in self.statements:
            for event in node.get_events( context ):
                yield event
    