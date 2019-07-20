from openloadwrapper import OpenloadWrapper

ID = "RCStnM-Qi4Q"


def main():
    wrapper = OpenloadWrapper("cb7f7c67392a22ac", "R_6Fd_vp")
    url = wrapper.get_thumbnail_when_ready(ID, 5)
    print(url)


if __name__ == '__main__':
    main()


