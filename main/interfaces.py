import abc

# interface for managing friendship
class FriendshipManager(metaclass=abc.ABCMeta):
   
    @abc.abstractmethod
    def add_friend(self,user,friend):
        pass

    @abc.abstractmethod
    def remove_friend(self,user,friend):
        pass

    @abc.abstractmethod
    def get_friend_list(self,user):
        pass
    
