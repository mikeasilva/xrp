import commands2
import ntcore


class NetworkTables(commands2.Subsystem):
    def __init__(self, table: str = "XRP") -> None:
        """
        Initialize the network tables subsystem.
        """
        super().__init__()
        nti = ntcore.NetworkTableInstance.getDefault()
        self.table = nti.getTable(table)
        self.state = self.create_topic("state", "string")
        self.crash = self.create_topic("crash-avoidance-activated", "boolean")
        self.max_speed = self.create_topic("max-speed", "double")

    def create_topic(self, topic_name: str, topic_type: str) -> None:
        if topic_type == "boolean":
            pub = self.table.getBooleanTopic(topic_name).publish()
        elif topic_type == "integer":
            pub = self.table.getIntegerTopic(topic_name).publish()
        elif topic_type == "double":
            pub = self.table.getDoubleTopic(topic_name).publish()
        elif topic_type == "string":
            pub = self.table.getStringTopic(topic_name).publish()
        elif topic_type == "raw":
            pub = self.table.getRawTopic(topic_name).publish()
        elif topic_type == "boolean_array":
            pub = self.table.getBooleanArrayTopic(topic_name).publish()
        elif topic_type == "integer_array":
            pub = self.table.getIntegerArrayTopic(topic_name).publish()
        elif topic_type == "double_array":
            pub = self.table.getDoubleArrayTopic(topic_name).publish()
        else:
            raise ValueError(f"Unsupported topic type: {topic_type}")
        return pub

    def get(self, topic_name: str) -> None:
        """
        Get the value of a topic.
        """
        return self.table.getEntry(topic_name)