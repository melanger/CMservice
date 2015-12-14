from calendar import monthrange
from datetime import datetime, timedelta
import json
import logging

LOGGER = logging.getLogger(__name__)
TIME_PATTERN = "%Y %m %d %H:%M:%S"


def format_datetime(datetime: datetime, format=None) -> datetime:
    """
    :param datetime: A datetime object to format using a given pattern
    :param format: the format to use, if non is defined TIME_PATTERN will be used
    :return: Formatted datetime object
    """
    if not format:
        format = TIME_PATTERN
    time_string = datetime.strftime(format)
    return datetime.strptime(time_string, format)


class Consent(object):
    def __init__(self, id: str, attributes: list, month: int, timestamp: datetime=None):
        """

        :param id: Identifier for the consent
        :param timestamp: Datetime for when the consent where created
        :param month: The policy for how long the
        :param attributes: A list of attribute for which the user has given consent. None equals
               that consent has been given for all attributes
        """
        if not timestamp:
            timestamp = datetime.now()
        self.id = id
        self.timestamp = format_datetime(timestamp)
        self.attributes = attributes
        self.month = month

    @staticmethod
    def from_dict(dict: dict):
        """
        :param dict: The consent object as a dictionary
        :return: Consent object created from a dictionary
        """
        try:
            id = dict['consent_id']
            timestamp = datetime.strptime(dict['timestamp'], TIME_PATTERN)
            month = dict['month']
            attributes = json.loads(dict['attributes'])
            return Consent(id, attributes, month, timestamp=timestamp)
        except TypeError:
            LOGGER.warning("Failed to create consent object from dict: %s" % dict)
            return None

    def to_dict(self):
        """
        :return: Consent object presented as a dictionary
        """
        return {
            'consent_id': self.id,
            'timestamp': self.timestamp.strftime(TIME_PATTERN),
            'month': self.month,
            'attributes': json.dumps(self.attributes),
        }

    def __eq__(self, other) -> bool:
        """
        :return: If all attributes in the consent object matches this method will return True else
                 false.
        """
        return (
            isinstance(other, self.__class__) and
            self.id == other.id and
            self.timestamp == other.timestamp,
            self.month == other.month,
            self.attributes == other.attributes,
        )

    def get_current_time(self) -> datetime:
        """
        :return: The current datetime
        """
        return datetime.now()

    def has_expired(self, max_months):
        current_date = self.get_current_time()
        if ((Consent.monthdelta(self.timestamp, current_date) > max_months) or
                (Consent.monthdelta(self.timestamp, current_date) > self.month)):
            return True
        return False

    @staticmethod
    def monthdelta(start_date: datetime, current_date: datetime) -> int:
        """
        :param start_date: The first date FROM which the delta should be calculated
        :param current_date: The second date TO which the delta should be calculated
        :return: Number of months from start_date to current_date
        """
        if start_date > current_date:
            raise StartDateInFuture("The start date, %s, is after current date, %s" %
                                    (start_date, current_date))
        delta = 0
        while True:
            mdays = monthrange(start_date.year, start_date.month)[1]
            start_date += timedelta(days=mdays)
            if start_date <= current_date:
                delta += 1
            else:
                break
        return delta

class StartDateInFuture(Exception):
    pass
