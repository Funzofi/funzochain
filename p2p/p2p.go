package main

import "C"

import (
	"bufio"
	"context"
	"time"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/crypto"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/routing"
	"github.com/libp2p/go-libp2p/p2p/net/connmgr"

	"fmt"

	dht "github.com/libp2p/go-libp2p-kad-dht"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peerstore"
	"github.com/libp2p/go-libp2p/core/protocol"
	"github.com/libp2p/go-libp2p/p2p/security/noise"
	tls "github.com/libp2p/go-libp2p/p2p/security/tls"
	"github.com/multiformats/go-multiaddr"
)

var (
	h       host.Host
	priv    crypto.PrivKey
	ctx     context.Context
	cancel  context.CancelFunc
	connman *connmgr.BasicConnMgr
)

func main() {}

func Run(listenAddr *C.char) *C.char {
	ctx, cancel = context.WithCancel(context.Background())
	defer cancel()

	var err error

	priv, _, err = crypto.GenerateKeyPair(
		crypto.Ed25519, // Select your key type. Ed25519 are nice short
		-1,             // Select key length when possible (i.e. RSA).
	)
	if err != nil {
		panic(err)
	}

	connman, err = connmgr.NewConnManager(200, 400, connmgr.WithGracePeriod(time.Minute))
	if err != nil {
		panic(err)
	}

	h, err = libp2p.New(
		libp2p.Identity(priv),
		libp2p.ListenAddrStrings(C.GoString(listenAddr)),
		libp2p.ConnectionManager(connman),
		libp2p.Security(tls.ID, tls.New),
		libp2p.Security(noise.ID, noise.New),
		libp2p.NATPortMap(),
		libp2p.Routing(func(h host.Host) (routing.PeerRouting, error) {
			idht, err := dht.New(ctx, h)
			if err != nil {
				return nil, err
			}
			return idht, nil
		}),
	)
	if err != nil {
		panic(err)
	}
	fmt.Println("I am ", h.ID().Pretty())
	return GetPeerID()
}

//export GetPeerID
func GetPeerID() *C.char {
	return C.CString(h.ID().Pretty())
}

//export GetPeerAddrs
func GetPeerAddrs() *C.char {
	return C.CString(h.Addrs()[0].String())
}

//export CreateHandler
func CreateHandler(path *C.char, handler *func(*C.char)) {
	//Convert c.func to go function
	h.SetStreamHandler(protocol.ID(C.GoString(path)), func(s network.Stream) {
		rw := bufio.NewReadWriter(bufio.NewReader(s), bufio.NewWriter(s))
		go readData(&rw, handler)
	})
}

//export Start
func Start(listenAddr *C.char) *C.char {
	go Run(listenAddr)
	// Check if h is initialised
	for h == nil {
		time.Sleep(1 * time.Second)
	}
	return GetPeerID()
}

//export Connect
func Connect(addr *C.char) {
	maddr, err := multiaddr.NewMultiaddr(C.GoString(addr))
	if err != nil {
		panic(err)
	}

	h.Peerstore().AddAddr(h.ID(), maddr, peerstore.PermanentAddrTTL)

	s, err := h.NewStream(context.Background(), h.ID(), "/chat/1.0.0")
	if err != nil {
		panic(err)
	}

	// Create a buffer stream for non blocking read and write.
	rw := bufio.NewReadWriter(bufio.NewReader(s), bufio.NewWriter(s))

	go readData(&rw, nil)

	// stream 's' will stay open until you close it (or the other side closes it).
}

//export Stop
func Stop() {
	cancel()
}

//export Hello
func Hello() *C.char {
	return C.CString("Hello from Go!")
}

func readData(rw **bufio.ReadWriter, handler *func(*C.char)) {
	for {
		str, _ := (*rw).ReadString('\n')
		if str != "" {
			if handler != nil {
				(*handler)(C.CString(str))
			} else {
				fmt.Print(str)
			}
		}
	}
}
