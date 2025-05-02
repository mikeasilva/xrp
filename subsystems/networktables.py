import commands2
import ntcore


class NetworkTables(commands2.Subsystem):
    def __init__(self, table: str = "XRP") -> None:
        """
        Initialize the network tables subsystem.
        """
        super().__init__()
        nti = ntcore.NetworkTableInstance.getDefault()
        self.nti_table = nti.getTable(table)
        self.state_pub = self.create_topic("state", "string")
        self.crash_pub = self.create_topic("crash-avoidance-activated", "boolean")

    def create_topic(self, topic_name: str, topic_type: str) -> None:
        if topic_type == "boolean":
            pub = self.nti_table.getBooleanTopic(topic_name).publish()
        elif topic_type == "integer":
            pub = self.nti_table.getIntegerTopic(topic_name).publish()
        elif topic_type == "double":
            pub = self.nti_table.getDoubleTopic(topic_name).publish()
        elif topic_type == "string":
            pub = self.nti_table.getStringTopic(topic_name).publish()
        elif topic_type == "raw":
            pub = self.nti_table.getRawTopic(topic_name).publish()
        elif topic_type == "boolean_array":
            pub = self.nti_table.getBooleanArrayTopic(topic_name).publish()
        elif topic_type == "integer_array":
            pub = self.nti_table.getIntegerArrayTopic(topic_name).publish()
        elif topic_type == "double_array":
            pub = self.nti_table.getDoubleArrayTopic(topic_name).publish()
        else:
            raise ValueError(f"Unsupported topic type: {topic_type}")
        return pub
