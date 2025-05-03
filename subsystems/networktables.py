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
        self.state = self.create("state", "string")
        self.crash = self.create("crash-avoidance-activated", "boolean")
        self.max_speed = self.create("max-speed", "double")
        self.x = self.create("x", "double")
        self.y = self.create("y", "double")
        self.z = self.create("z", "double")

    def create(self, topic_name: str, topic_type: str) -> None:
        if topic_type == "boolean":
            topic = self.table.getBooleanTopic(topic_name).publish()
        elif topic_type == "integer":
            topic = self.table.getIntegerTopic(topic_name).publish()
        elif topic_type == "double":
            topic = self.table.getDoubleTopic(topic_name).publish()
        elif topic_type == "string":
            topic = self.table.getStringTopic(topic_name).publish()
        elif topic_type == "raw":
            topic = self.table.getRawTopic(topic_name).publish()
        elif topic_type == "boolean_array":
            topic = self.table.getBooleanArrayTopic(topic_name).publish()
        elif topic_type == "integer_array":
            topic = self.table.getIntegerArrayTopic(topic_name).publish()
        elif topic_type == "double_array":
            topic = self.table.getDoubleArrayTopic(topic_name).publish()
        else:
            raise ValueError(f"Unsupported topic type: {topic_type}")
        return topic

    def read(self, topic_name: str) -> None:
        """
        Get the value of a topic.
        """
        return self.table.getEntry(topic_name)