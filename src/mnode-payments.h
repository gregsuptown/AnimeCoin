// Copyright (c) 2018 airk42
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.


#ifndef MASTERNODEPAYMENTS_H
#define MASTERNODEPAYMENTS_H

#include "vector"
#include "map"

extern CCriticalSection cs_vecPayees;
extern CCriticalSection cs_mapMasternodeBlockPayees;
extern CCriticalSection cs_mapMasternodePayeeVotes;

class CMasternodePaymentVote;

static const int MNPAYMENTS_SIGNATURES_REQUIRED         = 6;
static const int MNPAYMENTS_SIGNATURES_TOTAL            = 10;

static const int MIN_MASTERNODE_PAYMENT_PROTO_VERSION_2 = 70208;


class CMasternodePayee
{
private:
    CScript scriptPubKey;
    std::vector<uint256> vecVoteHashes;

public:
    CMasternodePayee() :
        scriptPubKey(),
        vecVoteHashes()
        {}

    CMasternodePayee(CScript payee, uint256 hashIn) :
        scriptPubKey(payee),
        vecVoteHashes()
    {
        vecVoteHashes.push_back(hashIn);
    }

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action, int nType, int nVersion) {
        READWRITE(*(CScript*)(&scriptPubKey));
        READWRITE(vecVoteHashes);
    }

    CScript GetPayee() { return scriptPubKey; }

    void AddVoteHash(uint256 hashIn) { vecVoteHashes.push_back(hashIn); }
    std::vector<uint256> GetVoteHashes() { return vecVoteHashes; }
    int GetVoteCount() { return vecVoteHashes.size(); }

};

// Keep track of votes for payees from masternodes
class CMasternodeBlockPayees
{
public:
    int nBlockHeight;
    std::vector<CMasternodePayee> vecPayees;

    CMasternodeBlockPayees() :
        nBlockHeight(0),
        vecPayees()
        {}
    CMasternodeBlockPayees(int nBlockHeightIn) :
        nBlockHeight(nBlockHeightIn),
        vecPayees()
        {}

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action, int nType, int nVersion) {
        READWRITE(nBlockHeight);
        READWRITE(vecPayees);
    }

    void AddPayee(const CMasternodePaymentVote& vote);
    bool GetBestPayee(CScript& payeeRet);
    bool HasPayeeWithVotes(const CScript& payeeIn, int nVotesReq);

    bool IsTransactionValid(const CTransaction& txNew);

    std::string GetRequiredPaymentsString();
};

// vote for the winning payment
class CMasternodePaymentVote
{
public:
    CTxIn vinMasternode;

    int nBlockHeight;
    CScript payee;
    std::vector<unsigned char> vchSig;

    CMasternodePaymentVote() :
        vinMasternode(),
        nBlockHeight(0),
        payee(),
        vchSig()
        {}

    CMasternodePaymentVote(COutPoint outpointMasternode, int nBlockHeight, CScript payee) :
        vinMasternode(outpointMasternode),
        nBlockHeight(nBlockHeight),
        payee(payee),
        vchSig()
        {}

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s, Operation ser_action, int nType, int nVersion) {
        READWRITE(vinMasternode);
        READWRITE(nBlockHeight);
        READWRITE(*(CScript*)(&payee));
        READWRITE(vchSig);
    }

    uint256 GetHash() const {
        CHashWriter ss(SER_GETHASH, PROTOCOL_VERSION);
        ss << *(CScript*)(&payee);
        ss << nBlockHeight;
        ss << vinMasternode.prevout;
        return ss.GetHash();
    }

    bool Sign();
    bool CheckSignature(const CPubKey& pubKeyMasternode, int nValidationHeight, int &nDos);

    bool IsValid(CNode* pnode, int nValidationHeight, std::string& strError);
    void Relay();

    bool IsVerified() { return !vchSig.empty(); }
    void MarkAsNotVerified() { vchSig.clear(); }

    std::string ToString() const;
};

class CMasternodePayments
{
protected:
    std::string GetGovernanceAddressAtHeight(int nHeight) const;
    CScript GetGovernanceScriptAtHeight(int nHeight) const;

public:
    std::map<uint256, CMasternodePaymentVote> mapMasternodePaymentVotes;
    std::map<int, CMasternodeBlockPayees> mapMasternodeBlockPayees;


    CAmount GetMasternodePayment(int nHeight, CAmount blockValue);
    void FillGovernancePayment(CMutableTransaction& txNew, int nBlockHeight, CAmount blockReward, CTxOut& txoutGovernanceRet);
    void FillMasterNodePayment(CMutableTransaction& txNew, int nBlockHeight, CAmount blockReward, CTxOut& txoutMasternodeRet);

    bool GetBlockPayee(int nBlockHeight, CScript& payee);


    bool HasPayeeWithVotes(const CScript& payeeIn, int nVotesReq) {return true;}
    bool IsScheduled(CMasternode& mn, int nNotBlockHeight) {return true;}
    void RequestLowDataPaymentBlocks(CNode* pnode) {}
    bool HasVerifiedPaymentVote(uint256 hashIn) {return true;}
    int GetStorageLimit() {return 0;}
    bool IsEnoughData() {return true;}
};

#endif