import commands2
import ntcore


class NetworkTables(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        self.nt = ntcore.NetworkTableInstance.getDefault()
        self.table = self.nt.getTable("XRPRobot")

    def get_entry(self, entry: str) -> ntcore.NetworkTableEntry:
        """
        Get the entry from the NetworkTables.

        :param entry: The name of the entry to get.
        :return: The NetworkTableEntry object.
        """
        return self.table.getEntry(entry)

    def set_entry(self, entry: str, value: any) -> None:
        """
        Set the entry in the NetworkTables.

        :param entry: The name of the entry to set.
        :param value: The value to set.
        """
        self.table.getEntry(entry).setValue(value)
