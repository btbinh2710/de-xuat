const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();

// Middleware
app.use(express.json());

// Cấu hình CORS
app.use(cors({
    origin: 'https://btbinh2710.github.io',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Danh sách người dùng giả lập
const users = [
    { username: 'admin', password: bcrypt.hashSync('admin123', 10), role: 'admin', branch: 'All' },
    { username: 'xdv_thaodien_manager1', password: bcrypt.hashSync('manager123', 10), role: 'manager', branch: 'XDV' }
];

// Danh sách đề xuất giả lập
let proposals = [
    { id: 1, proposer: 'Nguyễn Văn A', department: 'KD', date: '2025-05-01', code: 'DX001', proposal: 'Mua laptop', content: 'Mua laptop phục vụ công việc', supplier: 'Công ty ABC', estimated_cost: 15000000, approved_amount: 0, notes: '', completed: '', branch: 'XDV' }
];

const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Token required' });

    jwt.verify(token, 'your-secret-key', (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token' });
        req.user = user;
        next();
    });
};

app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;
    const user = users.find(u => u.username === username);

    if (!user) {
        return res.status(401).json({ error: 'Tên đăng nhập hoặc mật khẩu không đúng!' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
        return res.status(401).json({ error: 'Tên đăng nhập hoặc mật khẩu không đúng!' });
    }

    const token = jwt.sign({ username: user.username, role: user.role, branch: user.branch }, 'your-secret-key', { expiresIn: '1h' });
    res.json({ token, role: user.role, branch: user.branch });
});

app.get('/api/proposals', authenticateToken, (req, res) => {
    if (req.user.role === 'admin') {
        res.json(proposals);
    } else {
        const userProposals = proposals.filter(proposal => proposal.branch === req.user.branch);
        res.json(userProposals);
    }
});

app.post('/api/proposals', authenticateToken, (req, res) => {
    if (req.user.role === 'admin') {
        return res.status(403).json({ error: 'Admin không thể thêm đề xuất!' });
    }

    const newProposal = {
        id: proposals.length + 1,
        ...req.body,
        branch: req.user.branch
    };
    proposals.push(newProposal);
    res.status(201).json(newProposal);
});

app.put('/api/proposals/:id', authenticateToken, (req, res) => {
    const proposalId = parseInt(req.params.id);
    const proposalIndex = proposals.findIndex(p => p.id === proposalId);

    if (proposalIndex === -1) {
        return res.status(404).json({ error: 'Đề xuất không tồn tại!' });
    }

    if (req.user.role !== 'admin' && proposals[proposalIndex].branch !== req.user.branch) {
        return res.status(403).json({ error: 'Bạn không có quyền chỉnh sửa đề xuất này!' });
    }

    proposals[proposalIndex] = { ...proposals[proposalIndex], ...req.body };
    res.json(proposals[proposalIndex]);
});

app.delete('/api/proposals/:id', authenticateToken, (req, res) => {
    const proposalId = parseInt(req.params.id);
    const proposalIndex = proposals.findIndex(p => p.id === proposalId);

    if (proposalIndex === -1) {
        return res.status(404).json({ error: 'Đề xuất không tồn tại!' });
    }

    if (req.user.role !== 'admin' && proposals[proposalIndex].branch !== req.user.branch) {
        return res.status(403).json({ error: 'Bạn không có quyền xóa đề xuất này!' });
    }

    proposals.splice(proposalIndex, 1);
    res.status(204).send();
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});